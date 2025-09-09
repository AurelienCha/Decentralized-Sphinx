# Physical Implementation of a Mixnet Infrastructure

## Practical informations

**Computer science project** <br>
- Promotor: Jean-Michel Dricot & Jan Tobias Mühlberg <br>
- Supervisors: Aurélien Chassagne <br>
- Student’s background: Computer engineering or Computer science,  <br>
- Type : Computer science project / Internship <br>

## Motivation
![Mixnet topology](images/mixnet_comparison.png)

A mixnet (or mix network) is an overlay network of servers, called mixnodes, designed to prevent adversaries from correlating senders with receivers. Mixnets are a technology for achieving strong anonymity and unlinkability in digital communications. Unlike TOR (The Onion Router), where all packets in a session follow the same circuit (circuit-based), mixnets route each packet independently along different paths (packet-based). This makes traffic analysis significantly more difficult. To further enhance resistance against surveillance, mixnets employ techniques such as packet shuffling, reordering, and the injection of fake packets, aiming to resist even powerful adversaries capable of observing the entire network.
A key element of mixnets is the Sphinx packet format, which provides crucial properties such as fixed-size packets, layered encryption, and integrity verification. While standard encryption protects only message content, mixnets also care about metadata (e.g. who communicates with whom). In the age of large-scale data collection and artificial intelligence, metadata can be exploited to reveal sensitive information. Thus, mixnets are highly relevant beyond academic research, serving as the foundation for modern privacy-preserving communication systems.


## Project Description

In this project, you will design and implement a physical 3×3 mixnet infrastructure. This prototype will serve as a foundation for future research projects on privacy-preserving communication.

The student will be responsible for:
- Building functional mixnodes using Raspberry Pi (or similar hardware).
- Implementing the necessary networking and cryptographic components.
- Testing and validating the performance of the system.

### Recommended Skills and Interests

- Programming in Python or C++
- Basic hardware experience (e.g. Raspberry Pi)
- Network notions (e.g. \[ELEC-H417\] Communication Networks: Protocols and Architectures)
- Cryptography notions (e.g. \[INFO-F405\] Introduction to Cryptography)

### Useful Documentation

- Mixnets
    - [Nym Mixnet](https://nym.com/trust-center/papers-and-research)
    - [Katzenpost](https://katzenpost.network/)
- [Sphinx Packet Format](https://www.researchgate.net/publication/220713667_Sphinx_A_Compact_and_Provably_Secure_Mix_Format)

## Contact / Questions

[aurelien.chassagne@ulb.be](mailto:aurelien.chassagne@ulb.be)
