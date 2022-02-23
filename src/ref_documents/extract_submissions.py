import os
from shutil import copyfile

for university in os.listdir("./data/submission_batch"):
    print("Copying submissions from {}".format(university))
    if not os.path.isdir("./data/submissions/{}".format(university)):
        os.mkdir("./data/submissions/{}".format(university))
    for submission in os.listdir("./data/submission_batch/{}/ImpactCaseStudy".format(university)):
        source_dir = "./data/submission_batch/{}/ImpactCaseStudy/{}".format(university, submission)
        target_dir = "./data/submissions/{}/{}".format(university, submission)
        copyfile(source_dir, target_dir)
    print("Done")