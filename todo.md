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