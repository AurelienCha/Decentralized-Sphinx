# Guideline
- 13 pages ?
- For EuroS&P submission: publish code in anonymous Github (https://anonymous.4open.science/)
- For EuroS&P submission: use the special EuroS&P IEEE template (not the ACM from previous conf.)

# TODO
- Remove any suggestion if "legitimacy verification" properties. It should be mention only in introduction for motivation (and future work) but nowhere else (it is not the focus of our paper)
- Do not consider a 'virtual adversary' (i.e. "Malicious TTP/Mixnode" instead of "Collusion with TTP/Mixnode")
- Instead of TRUSTED third parties (TTP), we should speak of SEMI-TRUSTED third parties (STTP)

# Feedback / Questions

### Main
- How to insert section 5 in the new article version

### Secondary
- Remove any mention of "Relationship anonimity" (it is only for completness, does not bring useful information)


# Notes

## Small sub-group attack (Elligator)

- Generators: [WARNING] Must taken into since Generators are multiplied by secrets (leaking 3 bits)
- IP addresses: [OK] It is fine since only used in EC addition [NOTE] could have an impact in the scheme is changer (e.g. if modular inverse is needed)

## Secret sharing: Additive shares (not secret Shamir i.e. threshold)


# Meeting 12/11 with Iness
2.1 Reseaux decentralize (mixnet & Lightning network)
2.2 Packet format (TOR et Sphinx)

4. Repasser dessus (from 4.2 Client until section 5)


# Todo (thursday)
- Putting section 6.0 in threat model instead (section 3)
- Rewritte section 3
    3. Remove credential stuff
    3.1 Remove credentials. Et parler de STTP à la place ?
    3.2 plus développé
    3.3 Section 3 (threat model) ou section 6 (security)
- Section 3 is too "bullet point" put more context

- Merge section 6 and 7 (NIST and Complexity) into one section "Implementation Evaluation"