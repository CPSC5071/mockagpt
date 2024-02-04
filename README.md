## Description

Intended to generate fictional test data for a school project using ChatGPT API, e.g. 

| Movie Name | Movie Description | Movie Genre | 
|------------|-------------------|-------------|
| Catman | Catman does Catman things | Action |

Name is a reference to [Mockaroo](https://www.mockaroo.com/)

## Quickstart

Create a `.env` file containing below

```
OPENAI_API_KEY=<KEY>
```

Make sure you have balance in your [OpenAI account](https://platform.openai.com/account/billing/overview)

## Troubleshooting

### 1. Keep getting an error "You exceeded your current quota ..." despite having balance

If recently topped-up, recreate the API key


## TODO 

1. Turn into a site: 
   1. Password protect for cost reasons
   2. 2 Inputs: 
      1. Row number
      2. List of columns
   3. Show progress bar
   4. Downloads CSV when done
   5. Host the site in rpi, configure reverse proxy

2. If large number of CSV, batch the calls to OpenAI then combine results at the end 
   1. At the site, if batching, progress bar increases incrementally (e.g. 5 batches: 0% -> 20% -> 40% etc)

3. STRETCH GOAL: Allow uploading MySQL schemas and generate full e2e test data