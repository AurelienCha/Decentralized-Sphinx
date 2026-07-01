git clone --recurse-submodules https://github.com/your-org/your-repo.git

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