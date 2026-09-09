[Read CSV Row] ──> Are URL, Key, or Secret empty?
                     │
                     ├──> YES ──> Mark as Invalid (False)
                     │
                     └──> NO  ──> Send 'list_rooms' request to LiveKit server
                                    │
                                    ├──> Server accepts it? ──> Mark as Valid (True)
                                    │
                                    └──> Server throws error? ─> Mark as Invalid (False)