



# # printing data line by line
# indecesRm = []
# nb_row = len(participants)
# nb_col = len(participants[0])
# for row in range(nb_row):
#     for col in range(nb_col):
#         if col % nb_col == 0:
#             participantPath = Path(os.path.join(bidsPath, str(participants[row][col])))
#             if not participantPath.exists() or not list(participantPath.rglob('*.edf')) \
#                     or not list(participantPath.rglob('*electrodes.tsv')) \
#                     or not list(participantPath.rglob('*channels.tsv')) \
#                     or not list(participantPath.rglob('*events.tsv')):
#                 self.rejectedPart.append(str(participants[row][col]))
#                 indecesRm.append(row)
# for i in sorted(indecesRm, reverse=True):
#     del participants[i]


#montage = mne.channels.make_standard_montage('standard_1005')
#print("This the montage {}", montage.ch_names)
#raw.set_montage(montage, on_missing='ignore')