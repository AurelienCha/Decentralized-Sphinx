
def run_original_sphinx(iterations=7168, data_directory = 'src/experiments/data'):
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    # -*- coding: utf-8 -*-
    """
    The ``sphinxmix`` package implements the Sphinx mix packet format core cryptographic functions.

    The paper describing sphinx may be found here:

        * George Danezis and Ian Goldberg. Sphinx: A Compact and Provably Secure Mix Format. IEEE Symposium on Security and Privacy 2009. [`link <http://www.cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf>`_]


    All the ``sphinxmix`` cryptography is encapsulated and within a ``SphinxParams`` object that 
    is used by all subsequent functions. To make ``sphinxmix`` use different cryptographic 
    primitives simply extend this class, or re-implement it. The default cryptographic primitives 
    are ``NIST/SEGS-p224`` curves, ``AES`` and ``SHA256``.

    Sending Sphinx messages
    -----------------------

    To package or process sphinx messages create a new ``SphinxParams`` object:
    """
    # Instantiate a the crypto parameters for Sphinx.
    from sphinx_Danezis_git.sphinxmix.SphinxParams import SphinxParams
    params = SphinxParams()

    from random import randint
    NBR_MIXNODES = 20   # default: 10
    LENGTH_PATH = 5     # default: 5

    def save(header, data_directory, file):
        def binarize(header):
            alpha = f"{int(header[0].export(form=POINT_CONVERSION_COMPRESSED).hex(), 16):0226b}"
            beta = f"{int(header[1].hex(), 16):01280b}"
            gamma = f"{int(header[2].hex(), 16):0128b}"
            return alpha + beta + gamma
    
        with open(f"{data_directory}/{file}.data",'a') as f:
            f.write(binarize(header))

    """
    The ``sphinxmix`` package requires some rudimentary Public Key Information: mix nodes need
    an identifier created by ``Nenc`` and the PKI consists of a dictionary mapping node names
    to ``pki_entry`` records. Those include secret keys (derived using ``gensecret``) and public 
    keys (derived using ``expon``).
    """
    # The minimal PKI involves names of nodes and keys 
    from sphinx_Danezis_git.sphinxmix.SphinxClient import pki_entry, Nenc
    pkiPriv = {}
    pkiPub = {}
    for i in range(NBR_MIXNODES):
        nid = i
        x = params.group.gensecret()
        y = params.group.expon(params.group.g, [ x ])
        pkiPriv[nid] = pki_entry(nid, x, y)
        pkiPub[nid] = pki_entry(nid, None, y)


    # The simplest path selection algorithm and message packaging 
    from sphinx_Danezis_git.sphinxmix.SphinxClient import rand_subset, create_forward_message
    from sphinx_Danezis_git.sphinxmix.SphinxClient import PFdecode, Relay_flag, Dest_flag, Surb_flag, receive_forward
    from sphinx_Danezis_git.sphinxmix.SphinxNode import sphinx_process
    from petlib.ec import POINT_CONVERSION_COMPRESSED
    from tqdm import tqdm

    for it in tqdm(range(iterations)):
        """
        A client may package a message using the Sphinx format to relay over a number of mix servers. 
        The function ``rand_subset`` may be used to select a random number of node identifiers; the function
        ``create_forward_message`` can then be used to package the message, ready to be sent to the 
        first mix. Note both destination and message need to be ``bytes``.
        """


        use_nodes = rand_subset(pkiPub.keys(), LENGTH_PATH)
        nodes_routing = list(map(Nenc, use_nodes))
        keys_nodes = [pkiPub[n].y for n in use_nodes]
        dest = f"{randint(1, 2**127):0127b}"
        message = b"This is a test"
        header, delta = create_forward_message(params, nodes_routing, keys_nodes, dest, message)
        """
        The client may specify any information in the ``nodes_routing`` list, that will
        be passed to intermediate mixes. At a minimum this should include information about 
        the next mix.

        Processing Sphinx messages at a mix
        -----------------------------------

        The heart of a Sphinx mix server is the ``sphinx_process`` function, that takes the server
        secret and decodes incoming messages. In this example the message encode above, is decoded
        by the sequence of mixes.
        """
        # Process message by the sequence of mixes

        x = pkiPriv[use_nodes[0]].x
        i = 0
        while True:
            save(header, data_directory, 'original')   # save header
            i += 1
            ret = sphinx_process(params, x, header, delta)
            (tag, info, (header, delta), mac_key) = ret
            routing = PFdecode(params, info)
            if routing[0] == Relay_flag:
                flag, addr = routing
                x = pkiPriv[addr].x
            elif routing[0] == Dest_flag:
                save(header, data_directory, 'original')  # save header
                assert receive_forward(params, mac_key, delta) == [dest, message]
                break
