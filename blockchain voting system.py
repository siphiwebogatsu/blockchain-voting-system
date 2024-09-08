from pyteal import *

# Global state variables to store votes for each candidate
gugu_votes = App.globalGet(Bytes("gugu_votes"))
nthabi_votes = App.globalGet(Bytes("nthabi_votes"))
banele_votes = App.globalGet(Bytes("banele_votes"))
qhawe_votes = App.globalGet(Bytes("qhawe_votes"))
yonela_votes = App.globalGet(Bytes("yonela_votes"))

# Define the maximum number of votes allowed
max_votes = Int(20)  # Maximum 20 votes


# This sequence initializes the global state when the app is created
handle_creation = Seq(
    App.globalPut(Bytes("Votes"), Int(0)),
    App.globalPut(Bytes("gugu_votes"), Int(0)),
    App.globalPut(Bytes("nthabi_votes"), Int(0)),
    App.globalPut(Bytes("banele_votes"), Int(0)),
    App.globalPut(Bytes("qhawe_votes"), Int(0)),
    App.globalPut(Bytes("yonela_votes"), Int(0)),

    Approve(),
)

# Function to handle the voting logic
def vote_for_candidate(candidate: str):

     # Check if the sender has already voted (stored in local state)
    voter_status = App.localGet(Txn.sender(), Bytes("voted"))
    
    return Seq(
        # If the address has already voted, reject the transaction
        If(voter_status == Int(1),
           Reject(Bytes("Address has already voted")),
        ),

         # Ensure the total number of votes does not exceed the maximum allowed
        If(
            gugu_votes + nthabi_votes + banele_votes + qhawe_votes + yonela_votes < max_votes,
            Seq(

                # Mark the sender's address as having voted
                App.localPut(Txn.sender(), Bytes("voted"), Int(1)),  # Mark address as having voted
                App.globalPut(
                    Bytes("gugu_votes"),
                    If(candidate == "gugu", gugu_votes + Int(1), gugu_votes),
                ),
                App.globalPut(
                    Bytes("nthabi_votes"),
                    If(candidate == "nthabi", nthabi_votes + Int(1), nthabi_votes),
                ),
                App.globalPut(
                    Bytes("banele_votes"),
                    If(candidate == "banele", banele_votes + Int(1), banele_votes),
                ),
                App.globalPut(
                    Bytes("qhawe_votes"),
                    If(candidate == "qhawe", qhawe_votes + Int(1), qhawe_votes),
                ),
                App.globalPut(
                    Bytes("yonela_votes"),
                    If(candidate == "yonela", yonela_votes + Int(1), yonela_votes),
                ),
                Approve(),   # Approve the transaction if the vote is valid
            ),

            # Reject the transaction if the vote limit has been reached
            Reject(Bytes("Vote limit reached")),
        )
    )

# Function to read the vote counts for all candidates
def read_votes():
    return Seq([

        # Return the concatenated vote results for all candidates as a single outpu
        Return(Concat(
            Bytes("Gugu Votes: "), Itob(App.globalGet(Bytes("gugu_votes"))), Bytes("\n"),
            Bytes("Nthabi Votes: "), Itob(App.globalGet(Bytes("nthabi_votes"))), Bytes("\n"),
            Bytes("Banele Votes: "), Itob(App.globalGet(Bytes("banele_votes"))), Bytes("\n"),
            Bytes("Qhawe Votes: "), Itob(App.globalGet(Bytes("qhawe_votes"))), Bytes("\n"),
            Bytes("Yonela Votes: "), Itob(App.globalGet(Bytes("yonela_votes")))
        ))
    ])


# Define the application router
router = Router(
    "UCT Student Council Voting System",          # Name of the voting system
    BareCallActions(no_op=OnCompleteAction.create_only(handle_creation)),
)

# Method to handle voting action
@router.method
def vote(*, candidate: str):
    return vote_for_candidate(candidate)

# Method to read the current vote counts
@router.method
def read():
    return read_votes()

# Main function to compile and write the smart contract to files
if __name__ == "__main__":
    import os
    import json
    

    # Get the current path for saving the output files
    path = os.path.dirname(os.path.abspath(__file__))

    # Compile the approval and clear programs
    approval, clear, contract = router.compile_program(version=8)

    # Save the contract as a JSON file
    with open(os.path.join(path, "artifacts/contract.json"), "w") as f:
        f.write(json.dumps(contract.dictify(), indent=2))

    # Write out the approval and clear programs
    with open(os.path.join(path, "artifacts/approval.teal"), "w") as f:
        f.write(approval)

    with open(os.path.join(path, "artifacts/clear.teal"), "w") as f:
        f.write(clear)