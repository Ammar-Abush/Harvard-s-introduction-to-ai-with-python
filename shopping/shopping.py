import csv
import sys


from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    months={
            "Jan" : 0,
            "Feb" : 1,
            "Mar": 2,
            "Apr" : 3,
            "May": 4,
            "June" : 5,
            "Jul" : 6,
            "Aug":7,
            "Sep":8,
            "Nov": 9,
            "Oct":10,
            "Dec":11

        }
    with open(filename, 'r') as f:
        data = csv.reader(f)
        evidence = list()
        label = list()
        next(data)
        for row in data:
            ev = list()
            for i in range(17):
                if i == 0 or i == 2 or i == 4 or i == 11 or i == 12 or i == 13 or i == 14:
                    ev.append(int(row[i]))
                elif i == 15:
                    if row[i] == 'Returning_Visitor':
                        ev.append(1)
                    else:
                        ev.append(0)
                elif i == 16:
                    if row[i] == 'TRUE':
                        ev.append(1)
                    else:
                        ev.append(0)
                elif i == 10:
                    ev.append(months[row[10]])
                else:
                    ev.append(float(row[i]))
            evidence.append(ev)
            if row[17] == "TRUE":
                label.append(1)
            else:
                label.append(0)
    return (evidence,label)
 

        
            
        


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    knn = KNeighborsClassifier(n_neighbors=1)
    knn.fit(evidence, labels)
    return knn
    
    


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    sen = 0
    spec = 0
    totals = 0
    totalp = 0
    for l,p in zip(labels,predictions):
        if l == 1:
            totals+=1
            if l == p:
                sen+=1
        if l == 0:
            totalp+=1
            if l == p:
                spec+=1
        
    return(sen/totals, spec/totalp)
    


if __name__ == "__main__":
    main()
