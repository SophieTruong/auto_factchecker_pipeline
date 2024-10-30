- Create a python environment and activate

```
pip -m venv venv

source venv/bin/activate
```

- Install dependencies:

```
pip3 install -r requirements.txt

```

- There are 4 fack-checker websites available at the moment: Politifact, FactCheck.org, FullFact, and FaktaBaari. 
    
    - To update query word: change `query` values in the python script corresponding to one of the fack-checker website. For example, to update search query for Fackcheck.org, update `query` in factcheckorg.py: 
    
        ```
        query = "QUERY-STRING" 
        ``` 
    - Run `python3 factcheckorg.py` and the result will be print to terminal
