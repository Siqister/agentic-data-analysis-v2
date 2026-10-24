# spec: specs/indicators/points_reported_crime_incidents.md
# spec_hash: sha256:efc57ca2c1f8ccd64609ebd77b5933641eaa753be0739c2ded740630bba2f894
# generated: { by: claude-code, at: 2026-10-24T16:56:15-04:00 }
# verified: { by: human:siqi, at: 2026-10-24T17:59:48-04:00 }
"""Reported crime incidents (NIBRS Group A). Steps follow the spec's # Computation.

Returns the selected points (EPSG:3734) and the rows excluded at each step, by reason;
the runner writes them to build/points/."""

# cle_crime § NIBRS offense types: IncidentDesc values as spelled in the file.
GROUP_A = {
    "Aggravated Assault", "All Other Larceny", "Animal Cruelty", "Arson",
    "Assisting or Promoting Prostitution", "Bribery", "Burglary/Breaking and Entering",
    "Counterfeiting/Forgery", "Credit Card/Automatic Teller Fraud",
    "Destruction/Damage/Vandalism of Property", "Drug Equipment Violations", "Drug/narcotic Violations",
    "Embezzlement", "Extortion/Blackmail", "False Pretenses/Swindle/Confidence Game", "Forcible Fondling",
    "Forcible Rape", "Forcible Sodomy", "Gambling Equipment Violations", "Hacking/Computer Invasion",
    "Human Trafficking Commercial Sex Acts", "Human Trafficking Involuntary Servitude", "Identity Theft",
    "Impersonation", "Incest", "Intimidation", "Justifiable Homicide", "Kidnaping/Abduction",
    "Motor Vehicle Theft", "Murder and Nonnegligent Manslaughter", "Negligent Manslaughter",
    "Pocket-Picking", "Pornography/Obscene Material", "Purse-Snatching", "Robbery",
    "Sexual Assault With an Object", "Shoplifting", "Simple Assault", "Statutory Rape",
    "Stolen Property Offenses", "Theft From Building", "Theft From Coin Operated Machine or Device",
    "Theft From Motor Vehicle", "Theft of Motor Vehicle Parts/Accessories", "Weapon Law Violations",
    "Welfare Fraud", "Wire Fraud",
}
GROUP_B = {
    "All Other Offenses", "Bad Checks", "Disorderly Conduct", "Driving Under the Influence", "Drunkenness",
    "Family Offenses (Nonviolent)", "Liquor Law Violations", "Peeping", "Runaway",
    "Trespass of Real Property",
}
NOT_A_CRIME = "Justifiable Homicide"


def compute(ctx):
    # 1. The named fields.
    t = ctx.features(ctx.spec.meta["data"][0])
    excluded = {}

    def drop(mask, reason):
        nonlocal t
        excluded[reason] = int(mask.sum())
        t = t[~mask]

    # 2. Offense type. A value on neither list stops the run.
    unknown = sorted(set(t["IncidentDesc"].dropna()) - GROUP_A - GROUP_B)
    if unknown:
        ctx.stop(f"IncidentDesc values on neither the Group A nor the Group B list: {', '.join(unknown)}. "
                 "Add them to cle_crime § NIBRS offense types first.")
    drop(t["IncidentDesc"].isna(), "no IncidentDesc")
    drop(t["IncidentDesc"].isin(GROUP_B), "Group B offense")
    drop(t["IncidentDesc"] == NOT_A_CRIME, "Justifiable Homicide")

    # 3. Window, in local dates (applied by lib/).
    drop(t["OffenseDate"].isna(), "no offense date")
    drop(~ctx.in_window(t), "outside the window")

    # 4. One point per incident: the first row of each case.
    drop(t["CaseNumber"].isna(), "no case number")
    drop(t.duplicated("CaseNumber"), "additional offense in the same incident")

    # 5. Point rules.
    drop(t.geometry.isna() | t.geometry.is_empty, "no point")
    drop(~ctx.inside(t), "outside the clip extent")

    # 6. Output.
    return t[["CaseNumber", "OffenseDate", "geometry"]].reset_index(drop=True), excluded
