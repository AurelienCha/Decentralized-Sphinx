# CBT feedback

##  Possible Improvment

- The main concern is practicality. It is not clear where the trusted third parties responsible for route selection are expected to come from.
- The latency overhead should also be discussed in the limitations.
- The paper would also benefit from a stronger motivation for the decentralised construction. Client-controlled route selection also gives clients control over how their messages are routed and can be desirable.
- What is the difference between your two implementations of DSphinx?
-  In general, the path sampling and aggregation part could be better explained.

## Discussion

- Additionally, and this is something that the authors acknowledge as a limitation, while random path selection may benefit privacy, it is worth considering how DSphinx can be made more viable for a network like Lightning.
- It prevents the client to select the path. This might go against the nature of the Lightning Network (LN) if a client cannot select the payment path. 
It can have more implications in the working nature of the LN, privacy and security issues, which can be worst than the problem you are trying to solve.
- The path selection by the STTP is random, which is a way too oversimplified approach for LN. 
Although authors justify it by privacy issues, which is true.
But this justification is by no means clear, whether this will justify the potential loss in performance (fees, delays, etc.)
- **My main concern is with its applicability to payment channel networks.**
The fact that path selection is random, might be interesting in the context mixnets or even onion routing in general, but in the case of the LN seems a bit
more difficult. It improves privacy but the cost for doing so might be too big.












Client
# build_packet: p & t
## query_route: p & t (biggest overhead)
## shared_secret_rerandomization: p
## compute_layers: p**2

Mixnode
# setup: s, t (biggest overhead, but once)
# process_header: p
## compute_shared_secret: /
## verify_integrity: /
## decrypt_beta: p
## update_alpha: /

STTP
# store_share: /
# send_shares: /



# Todo:
Before setup could have the mixnodes communicating together (and send their pseudonyme) to build a map of network and send it to STTPs afterwards


