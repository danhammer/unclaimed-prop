## unclaimed-prop

Script to download unclaimed property data from https://ucpi.sco.ca.gov/ucp/Default.aspx

For now, go into the `scrape.py` buffer and run the `process_data()` function with one, required argument -- specifically, an integer of values to process.

```python
>>> process_data(1000)
uploading 17338524
uploading 1233362
uploading 13049574
...
```

OR run the following command from the command line:

```bash
python scrape.py -n 100
```
