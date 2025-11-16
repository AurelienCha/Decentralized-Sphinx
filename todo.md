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





# Todo (thursday)

- Add a ref for Elligator
- Check complexity table (hash, not to compute shared secret but weights)
- Reformulation for adversary advantage. Don't like the lmbda notation

- Style: subsection 4 "[Party] - [Function]" (e.g. 4.1. Setup - Independant generators, 4.2. Client - Additive shares, 4.3. STTP - Partial header, 4.4. Decryption and forward)

- Putting section 6.0 in threat model instead (section 3)
- Merge section 6 and 7 (NIST and Complexity) into one section "Implementation Evaluation"

- Propose mitigiation for collusion vulnerability
- Conclusion with future work
