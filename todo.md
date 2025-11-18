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


- Add a ref for Elligator
- Reformulation for adversary advantage. Don't like the lmbda notation

- Style: subsection 4 "[Party] - [Function]" (e.g. 4.1. Setup - Independant generators, 4.2. Client - Additive shares, 4.3. STTP - Partial header, 4.4. Decryption and forward)

- Propose mitigiation for collusion vulnerability
- Conclusion with future work

- Anonymous github and cleaning code (e.g. client)
