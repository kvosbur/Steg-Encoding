## Encoding

### Options
    -b <amount> : amount of bits to use per pixel to encode with
    -f <fileName/filePath> : path to file to be encoded.
    -s <directoryOfSourceImages> : directory of images to use.
    -d <directoryOfDestinationImages> : directory of destination images (will create if not found)
    

### Encryption
    - Input data file will be encrypted using AES GCM
        Note: this limits size of file to be encrypted to 68gb.
    - Encoding into given image file
        1) (first file) 
            - 1 byte describing method used
            - salt used for kdf
            - iv used for encryption
        2) (last file) n bits describing amount of bits written to file (n based on pixel size)
            n = log [base 2] ( total_pixels * 3 (or 6, depending on amount of lower order bits) )
        2) encrypted data

## Lessons
    - Can't save encoded image to .jpg since it has lossless compression.... Currently using png instead

## Open Questions
    - How many bits/bytes to use to describe image order?
    - Is it possible to hide image order well in metadata?
    - What is the best way to denote end of encrypted file?
        - Should I instead add field that specifies how much of the image is used?
    - Behavior of GCM (first time using)
        - need iv and it gives auth tag afterwards used for authenticating decryption
    - Should the bits describing order of images also be encrypted?
        - No since order matters for decryption for everything
        - Unless it is wanted for each picture to have its own iv/tag

## Goals
    - Secure file data so it is not easy to retrieve cryptographically
    - Obscure that the file is even hiding information

## Future
    - support using .mp4s instead (would not need image order set)
    - support different amount of lower order bits to use for encoding
    - support using multiple images to store a large file
    - support different encryption methods 
        - AES CBC (performance gains) 
            - Could set IV on every file where IV for later file is last block of prev
                Would mean that file boundaries would have to equal block boundaries
        - iv and hmac on a per file basis (performance gains)? (memory losses?)