# ReTube
An alternative front-end to `YouTube`, `Odysee/Lbry`, `Bitchute`, `Rumble`, etc.

Access all videos from one place. \
No account, no ads, no tracking. \
Subscriptions are saved locally in [`LocalStorage`](https://javascript.info/localstorage) (TODO: Optional `Sync`)

Mirrored at Gitlab: https://gitlab.com/PrivOci/ReTube

# DEMO
[![DEMO](https://user-images.githubusercontent.com/74867724/112172240-736d0780-8bec-11eb-97a8-61b1a7e9eba4.png)](https://streamable.com/zx1cpu)


# Development
I'm not a web developer and this one is my first project, if you like the idea please contribute, any kind of feedback is welcome. \
The frontend is build using [`NextJS`](https://nextjs.org) with [`Tailwinds`](https://tailwindcss.com). \
The backend uses [`FastApi`](https://fastapi.tiangolo.com) and [`Redis`](https://redis.io).

I chose them because they are very simple and easy-to-use.

# Setup local instance:
## Docker
`git clone https://github.com/PrivOci/ReTube` \
`cd ReTube` \
`docker-compose up -d`

# Manual:
# Backend
## Setup Redis for Caching

`cd backend/redis` \
`docker-compose up -d`

## FastApi
`cd backend` \
`pip3 install virtualenv` \
`python -m virtualenv venv` \
`venv\Scripts\activate` \
`pip install -r requirements.txt`
 
`uvicorn main:app --reload` or `python ./main.py` \
API docs: `http://localhost:8000/docs`

# Frontend
`cd frontend` \
`yarn` \
`yarn run dev`
