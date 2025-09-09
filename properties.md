MAIN GOAL:          Allow packet legitimacy verification                            [Not_yet_achieved]
SECONDARY GOAL:     Avoid biased path (should decentralized path selection)         [Not_yet_achieved]

# IMPORTANT REMARK - SCHEME MODIFICATION
For the security analysis, I would make a change in the schema proposed in our article (in the Client side).
The Client compute the share secrets (Eq. 2) using an hash function as pseudo-randomizer (to mimic original Sphinx).
Later, we would probably want to decentralized this computation (Eq. 2) to decentralized path selection.
In this case, the hash will be a problem.
Therefore I already modify it by removing the hash step.
I.e. x_{i+1}        =   s_i     *   x_i 
I.e. \alpha_{i+1}   =   s_i     *   \alpha{i}

# Hypothesis:
- At least one non-colluding mixnode in the path (if all mixnodes collude then anonymity is trivially broken)

# Adversary:
- GPA (Global passif adversary) => bitwise unlinkability
- GAA (Global active adversary) => alter or create packet
- Honest-but-curious TTP
- Malicious Client

# Properties

## Anonimity / Privacy
- [Fixed-size] (pre-requis for unlinkability)                                    [Implementation] OK
    => TRICK: "Filler chunks"
- [Bitwise_unlinkability] (or mix unlinkability)                           
    => Should look random from a cryptanalyse point of view                      [NIST_STATISTICAL_TEST_SUIT] OK                                    
    => Backdoor: Indep generators G_i (see security notes)                       [PROOF_NEEDED]  -> for the moment just a necessary condition                      
- [Relationship_anonimity] / [Sender_anonymity] & [Receiver_anonimity] 
- Unlinkability of a packet with the source, except at the first mixnode (or destination, except at the last mixnode)
    => Require [Bitwise_unlinkability] + mixnode cannot compute other s_i (previous path not possible, because need to compute secret 'x') [PROOF_NEEDED]
    - Eq 2 (x_{i+1} = x_i * r_i) => Need to use x_i (i.e. secret) to update alpha, just using r_i woulc allow a mixnode to compute following shared secrets, breaking the full schema => r_i is a pseudo randomizer 
    ==> IDEA: h(alpha||S) is it needed ? We could use s_i directly no ? (faster and get ride of hash) <==
- [Collusion_resistance]
    => Proove the minimal number of shares needed to infer some information      [PROOF_NEEDED]

## Robustness
- Integrity (any modification will be detected)                                                                                           [PROOF_NEEDED]
    => Pseudo-random weights: Avoid arbitrarily adding P to a chunk and substracting P to another chunks
    => Secret offset: Avoid TTP to be able to verify integrity tag (and therefore break unlinkability)
- Replay attack resistance
    => Mixnode has table of already seen ALPHA. If already seen ALPHA, then discard the packet (table is reset when mixnode private key changes)
    => Replay attack therefore need to change ALPHA and GAMMA such that integrity still hold                                                        [see_INTEGRITY] 
- Wrap resistance (if header H, cannot create header H' such that becomes header H later)                                                           [see_INTEGRITY] 

## Correctness:
- Correctness                                                                     [Implementation] OK
- Bounded path size                                                                 [PROOF_NEED]             
- Verifiability (legitimacy verification)                                         [Not_yet_achieved] -> MAIN GOAL




# Steps:

## Proof (1) "relationship anonimity" 
    - hypothesis: Bitwise unlinkability
    - proof:
        a) cannot find previous nodes: 
            proof: it means finding the root secret 'x'
        b) cannot find following nodes
            proof: reduced to compute next shared secret
    - require: x_i to update alpha (eq 2)

## Proof (2) "bitwise unlinkability":
    - Input: 2 Headers layer i and layer i+1 
    - proof: no more than 50% chance of linking the corresponding header
    - require: Indep generators
    - EXTRA: Cryptanalyse randomness (NIST test suite)

## Proof (3) "Collision resistance":
    - proof: minimal number of shares to infer info
    - 2 scenarios:
        a) TTP-TTP
        b) TTP-mixnode

## Proof (4) "Integrity":  (proof of 'replay resistance' and 'wrap resistance')
    NB: Developping GAMMA computation should hightlight degree of freedom that we have to modify it
    - proof: Cannot compute valid GAMMA when modifying the header 
    - require:
        - Pseudo-random weights => Avoid arbitrarily adding P to a chunk and substracting P to another chunks
        - Secret offset         => Avoid TTP to be able to verify integrity tag (and therefore break unlinkability)

## Proof (5) Bounded path size
    - proof: Is there any special case in which we could create an infinite loop header construction (with valid integrity tag)
