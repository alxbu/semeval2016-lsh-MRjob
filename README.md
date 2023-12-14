# semeval2016-lsh-MRjob

## Introduction

This is a MRJob implementation of the LSH algorithm for the SemEval 2016 Task 3: Community Question Answering.
The implementation runs LSH with different parameters (number of bands and rows) and outputs the results to a file.

## Setup

### 1. Create a virtual environment

```
virtualenv venv
```

### 2. Activate the virtual environment

```
source venv/bin/activate
```

### 3. Install the requirements

```
pip install -r requirements.txt
```

## How to run

Retrieve the data from the source. Preprocess the data. Run the job.

### 1. Get the data

```
./get_data.sh
```

### 2. Preprocess the data

```
python preprocess.py
```

### 3. Run the job

```
python lsh_mrjob_runner.py
```

### 4. Analyze the results

```
python analyze_results.py
python analyze_ground_truth.py
```

