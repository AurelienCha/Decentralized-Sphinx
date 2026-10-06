# Transcript Presentation

# Title slide
Good afternoon everyone.
I am pleased to present you my work, DSphinx: A Decentralized Path Selection for Decentralized Networks.

# Slide 1: Intro
As you probably already know, even when communication are encrypted, metadata still reveals who is communicating to whom.

# Slide 2: Mixnet
One way to address this problem is through privacy-preserving communication networks such as mixnets.
- A mixnet routes messages through several intermediate nodes, called mixnodes. Each mixnode collects packets, shuffles them, and forwards them in a different order.
- Each packets uses a differente route and have a fixed size.
- Those mechanisms, together, provide unlinkability, making it difficult to correlate senders with receivers, even for a strong global adversary.
- Let me briefly illustrate this with the animation.

# Slide 3: Problem
In those networks clients have full control over the route selection. 
- Therefore, it opens the door for malicious client to perform route-based manipulation attacks. Which can lead to anonimity-set reduction, packet tracing such as n-1 attack, and targeting specific mixnodes with Denial of Service or Reputation attacks.
- So this leads to our research question: How can we prevent route manipulation without compromising privacy?
- Our approach is to decentralize route sampling across semi-trusted third parties, or STTPs.

# Slide 4: Sphinx
Before presenting our construction, let me briefly explain the Sphinx packet format used in mixnets, since our route-selection mechanism has to remain compatible with it.
- A Sphinx packet consists of a header and a payload. The header contains three  elements: alpha, the cryptographic element; beta, the encrypting routing information; and gamma, the integrity tag.
- At mixnode i, the node uses its secret key k_i and the cryptographic element to derive a Diffie-Hellman shared secret S_i.
- This shared secret is used to verify the integrity, and decrypt the routing information, revealing the next hop, the next encrypted routing information, and the next integrity tag.
- The cryptographic element is then blinded, for unlinkability, before forwarding the packet.
- This means the shared secrets are derived in cascade, it will be important for later.
- In short, Sphinx provides per-hop confidentiality, per-hop integrity, and a fixed packet size.

# Slide 5: Overview
So now we can look at our decentralized route-selection procedure.
- Compared with a standard mixnet, we introduce a set of STTPs, or semi-trusted third parties.
- The protocol consists of three steps.
First, a setup phase, performed once between mixnodes and STTPs.
Then, for each packet, the client requests partial route information from a threshold number of STTPs.
Finally, the client aggregates these partial results to reconstruct a valid route and the corresponding shared secrets.
- Of course, the STTPs do not learn the route or the shared secrets.
- I will now explain these three steps.

# Slide 6: Setup
Let's start with the setup phase, which is performed once.
- Each mixnode i chooses a random identifier r_i, a secret key k_i, and its encoded address N_i.
- It then uses Shamir secret sharing to split both the secret key and the encoded address into shares.
- For each STTP, the mixnode evaluates the corresponding polynomials and sends the resulting shares.
- Each STTP stores these shares in a table indexed by the mixnode's random identifier.
- This gives each STTP only a partial view of the information needed for route sampling.

# Slide 7: Sampling
- During route sampling, the client sends the same nonce w to a threshold number of STTPs.
- For each hop, the STTP combines this nonce with a timestamp and the hop index, and hashes them to obtain a pseudorandom seed.
- This seed is used as a deterministic lookup in its setup table, selecting the row with the closest index.
- The STTP then derives a partial shared secret using its share of the corresponding secret key.
- Finally, it returns the partial encoded address and partial shared secret to the client.
- The important point is that each STTP provides only a partial contribution to the route.

# Slide 8: Aggregation
-Once the client has received responses from a threshold number of STTPs, it uses Lagrange interpolation to reconstruct the encoded addresses and shared secrets.
- However, there is a problem.
The reconstructed shared secrets are independent, whereas Sphinx requires them to be derived in cascade.
So we perform a cascade derivation over the reconstructed secrets.
- Where r is a fresh nonce used to rerandomizes the cryptographic element, preserving the unlinkability property.
- Finally, the client uses these values to construct the Sphinx packet as usual.

# Slide 9: Scalability
Now let's look at the client computational overhead.
- These two experiments vary the two main system parameters: route length and STTP threshold.
- We observe that the computation time increases approximately linearly with the route length, while the threshold experiment follows approximately an n log n behavior.
- At the largest tested configurations, the client computation reaches around 50 milliseconds, compared with roughly 1-2 milliseconds for original Sphinx.
- This is a non-negligible overhead, but it remains moderate compared with an end-to-end mixnet latency of around 500 to 800 milliseconds.

# Slide 10: Stage
This second experiment shows where the overhead comes from.
- The light-blue part corresponds to the standard Sphinx operations: packet construction by the client and packet processing by the mixnodes.
- The dark-blue part represents the additional computation introduced by our scheme.
- We can clearly see that the main overhead comes from two polynomial operations: Shamir secret sharing during mixnode setup, and Lagrange interpolation during client aggregation.
- In practice, the setup cost is paid only once, while the aggregation cost for each packet, which thereofre is the most important overhead.

# slide 12: Future Work
There are two main directions for future work.
- First, it would be interesting to compare our approach with alternative mechanisms, particularly ZK and VRF-based routing.
- Second, we could generalize the current random route-selection algorithm to support cost-based routing.
This would make the approach applicable to broader decentralized systems, including potential interest in blockchain networks.

# Slide 11: Takeaway
- To conclude, we proposed a way to prevent route manipulation by malicious clients without revealing the route, by decentralizing route sampling across STTPs.
- Our evaluation shows that the approach introduces additional computation, mainly from client aggregation step, but that the overall overhead remains moderate compared with typical end-to-end mixnet latency.


Thank you.

-------------- TIME CODE 12 min --------------