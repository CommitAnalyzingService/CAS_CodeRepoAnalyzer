from classifier.classifier import *
from caslogging import logging

logging.info('Test categorization... ')
classifier = Classifier()

# Test classification of corrective commits
# fix,bug,wrong,fail,problem

corrective_msg_1 = "fixed something"
corrective_msg_2 = "bam, there goes a bug!"
corrective_msg_3 = "x was wrong, but no more!"
corrective_msg_4 = "Houston, we *had* a problem"
corrective_msg_5 = "My watch is fun"
corrective_msg_6 = "This is definitively NOT a you-know what!"

assert(classifier.categorize(corrective_msg_1) == "Corrective")
assert(classifier.categorize(corrective_msg_2) == "Corrective")
assert(classifier.categorize(corrective_msg_3) == "Corrective")
assert(classifier.categorize(corrective_msg_4) == "Corrective")
assert(classifier.categorize(corrective_msg_5) != "Corrective")
assert(classifier.categorize(corrective_msg_6) != "Corrective")

# Test classification of feature additions
# new,add,requirement,initial,create

feature_msg_1 = "new awesome thing added to that brillinat code"
feature_msg_2 = "adding some color to this mundane gui!"
feature_msg_3 = "Adding requirement.."
feature_msg_4 = "This is an initial commit"
feature_msg_5 = "Creating a new class for x,y, AND z!"
feature_msg_6 = "This is definitively NOT a you-know what!"

assert(classifier.categorize(feature_msg_1) == "Feature Addition")
assert(classifier.categorize(feature_msg_2) == "Feature Addition")
assert(classifier.categorize(feature_msg_3) == "Feature Addition")
assert(classifier.categorize(feature_msg_4) == "Feature Addition")
assert(classifier.categorize(feature_msg_5) == "Feature Addition")
assert(classifier.categorize(feature_msg_6) != "Feature Addition")

# Test classification of preventative commits
# test,junit,coverage,assert

prev_msg_1 = "testing to make sure of stuff"
prev_msg_2 = "junit rocks, stay heavy!"
prev_msg_3 = "coverage is now much higher"
prev_msg_4 = "asserting that our code doesn't make computers 'splode"
prev_msg_5 = "I am totally awesome"

assert(classifier.categorize(prev_msg_1) == "Preventative")
assert(classifier.categorize(prev_msg_2) == "Preventative")
assert(classifier.categorize(prev_msg_3) == "Preventative")
assert(classifier.categorize(prev_msg_4) == "Preventative")
assert(classifier.categorize(prev_msg_5) != "Preventative")

# Test that corrective classification again
# fix,bug,wrong,fail,problem

corrective_msg_1 = "fixed something"
corrective_msg_2 = "bam, there goes a bug!"
corrective_msg_3 = "x was wrong, but no more!"
corrective_msg_4 = "Houston, we *had* a problem"
corrective_msg_5 = "My watch is fun"
corrective_msg_6 = "This is definitively NOT a you-know what!"

assert(classifier.categorize(corrective_msg_1) == "Corrective")
assert(classifier.categorize(corrective_msg_2) == "Corrective")
assert(classifier.categorize(corrective_msg_3) == "Corrective")
assert(classifier.categorize(corrective_msg_4) == "Corrective")
assert(classifier.categorize(corrective_msg_5) != "Corrective")
assert(classifier.categorize(corrective_msg_6) != "Corrective")

logging.info("Passed tests")