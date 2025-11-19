# Guideline
- 13 pages ?
- For EuroS&P submission: publish code in anonymous Github (https://anonymous.4open.science/)
- For EuroS&P submission: use the special EuroS&P IEEE template (not the ACM from previous conf.)

# Notes

## Small sub-group attack (Elligator)

- Generators: [WARNING] Must taken into since Generators are multiplied by secrets (leaking 3 bits)
- IP addresses: [OK] It is fine since only used in EC addition [NOTE] could have an impact in the scheme is changer (e.g. if modular inverse is needed)

## Secret sharing: Additive shares (not secret Shamir i.e. threshold)


# Todo (thursday)

- Propose mitigiation for collusion vulnerability [ATTENTION]

# TODO
- Reformulation for adversary advantage. Don't like the lambda notation
- Anonymous github and cleaning code (e.g. client) [IMPORTANT]
- Developper Elligator + ref

# Accesibility
- Section 4 (and 5): Reread this section and check for parts that could be unclear to add extra explanations.
- Pseudocode [IMPORTANT]

# General
- Try to avoid "mixnet" if not pertinent (e.g.)
- use the nomination of DSphinx (change figures as well)
- Layout: improve spacing and mise en page
- Equation format (x) and figure