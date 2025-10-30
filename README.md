# credential_extractor

# =============================================================================================================== #
<!-- 
HERE WE BASICALLY HAVE 3 FILES FOR BOTH LIVEKIT AND DEEPGRAM

LIVEKIT_SENDER, DEEPGRAM_SENDER  - FOR SENDING DATA TO UPSTASH VIA (POST) API

LIVEKIT_EXTRACTOR.PY, DEEPGRAM_EXTRACTOR.PY - FOR  EXTRACT THE CREDENTIALS 
    FOR LIVEKIT : CREDENTIALS EXTRACTED IS EMAIL, LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET

    FOR DEEPGRAM : CREDENTIALS EXTRACTED IS EMAIL, DEEPGRAM_API_KEY

LIVEKIT_KEYS, DEEPGRAM_KEYS : CONTAINING ALL THE REQUIRED CREDENTIALS THAT SAVED IN .csv FILE

-->

NOTE - LIVEKIT_KEYS.TXT, DEEPGRAM_KEYS.TXT FILE CONTAINING ALL THE REQUIRED CREDENTIALS 

# FOR LIVEKIT CREDENTIALS SEND TO UPSTASH WITH API OR UPSTASH_KEYS

1. RUN THE livekit_extractor.py using below command

# TO  EXTRACT THE CREDENTIALS FROM THE LIVEKIT_KEYS.TXT

    ```
        bash

        python livekit_extractor.py

    ```

THIS WILL MAKE LIVEKIT_DATA.CSV OR IF EXISTED THEN REWRITE IT 

2. RUN THE livekit_sender.py using below command 

    ```
        bash

        python livekit_sender.py
    
    ```

THIS WILL CHANGE CSV DATA TO JSON IN THIS FORMART email,LIVE_KIT_URL,LIVEKIT_API_KEYS,LIVEKIT_SECRET_KEYS AND SEND TO * UPSTASH *

# FOR DEEPGRAM CREDENTIALS SEND TO UPSTASH WITH API OR UPSTASH_KEYS



1. RUN THE deepgram_extractor.py using below command

# TO EXTRACT THE CREDENTIALS FROM THE DEEPGRAM_KEYS.TXT

    ```
        bash

        python deepgram_extractor.py

    ```

THIS WILL MAKE DEEPGRAM_DATA.CSV OR IF EXISTED THEN REWRITE IT 

2. RUN THE deepgram_sender.py using below command 

    ```
        bash

        python deepgram_sender.py
    
    ```

THIS WILL CHANGE CSV DATA TO JSON IN THIS FORMART email,LIVE_KIT_URL,LIVEKIT_API_KEYS,LIVEKIT_SECRET_KEYS AND SEND TO * UPSTASH *

# =========================================================================================================================================== #








