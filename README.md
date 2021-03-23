# ReTube
Access videos from `YouTube`, `Lbry/Odysee` and `Bitchute` from a one place. \
No account, no ads, no tracking. \
Subscriptions are saved locally in [`LocalStorage`](https://javascript.info/localstorage) (TODO: Optional `Sync`)

# DEMO
[![DEMO](https://user-images.githubusercontent.com/74867724/112172240-736d0780-8bec-11eb-97a8-61b1a7e9eba4.png)](https://www.youtube.com/watch?v=WpcB_A-mZLY)


# Development
## Backend
`cd backend` \
`pip3 install virtualenv` \
`python -m virtualenv venv` \
`venv\Scripts\activate` \
`pip install -r requirements.txt`

API docs: `http://localhost:8000/docs`

## Setup Redis for Caching

`cd backend/redis` \
`docker-compose up -d`


## Frontend
`cd frontend` \
`yarn` \
`yarn start`