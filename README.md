# Houzz Website Scrapper

# About project infrastructure
```
    The project is divided into two parts.
    
    1) Crawler, which takes search result page url as a parameter, and crawls all available profile URLs from search result page,
    registers new celery task for each profile and waits for response to write scrapped json object results into the file in parallel mode.
    
    2) Scrapper Task, this is nothing but just a scrapper, trigerred when new pages are added into queue. returns a json string as a result.
```

# How to run
```
    Just make sure that you've docker and docker compose installed on your machine.
    
    1) make setup - it will build images and install all required data for containers.
    2) make start - it will run scrapper, you will be promped for entering URL and total pages you want to scrap.
    
    example URL: https://www.houzz.com/professionals/general-contractor/san-francisco-ca-us-probr0-bo~t_11786~r_5391959
```

# Take into account
```
    Average time for scraping 10 pages can take up to 4-6 minutes, as we have code-level delays while proxies aren't configured yet.
    Currently, error handlings aren't well-optimized (not giving well valuable info at all), probably I will improve it.
    
    You can follow the application logs and results in live for sure:
    tail -f results.jsonl
    tail -f app.logs
```
