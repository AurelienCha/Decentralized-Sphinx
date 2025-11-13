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
1. INTRODUCITON
2. MOTIVATION
3. MODEL
4. SCHEMA
5. EVULATION
6. SECURITY

2.1 Reseaux decentralize (mixnet & Lightning network)
2.2 Packet format (TOR et Sphinx)

3. Remove credential stuff
3.1 Remove credentials. Et parler de STTP à la place ?
3.2 plus développé
3.3 Section 3 (threat model) ou section 6 (security)

4. Repasser dessus
Remove 4.1 and section 4 becomes "Protocol Description"

5. Changer nom -> NIST
5.1 en dehors de section 5 (NIST)

Ordre:
Sec 4 - Schema
Sec 6 - Security
Sec 5 - "Evaluation" (complexity en dernier)