# Analysis checklist

- What is one row, and can the same real-world entity appear in multiple rows?
- Which columns were available at the moment a prediction or decision would be made?
- Are missing values random, structural, or a signal created by the process?
- Are train, validation, and test splits grouped or time-ordered where required?
- What baseline must a model beat to matter?
- Which metric matches the real cost of false positives and false negatives?
- Is the sample large enough for the claimed precision?
- Would the conclusion survive a reasonable alternative filter, seed, or model?
