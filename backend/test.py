from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# test /api/video - request video details


def test_get_video_yt():
    """ Test /api/video for Youtube. """
    response = client.post(
        "/api/video/",
        json={"id": "jNQXAC9IVRw", "platform": "yt"},
    )
    assert response.status_code == 200
    json_object = response.json()
    assert json_object["ready"] == True
    assert json_object["platform"] == 'yt'
    assert json_object["content"]["id"] == 'jNQXAC9IVRw'
    assert json_object["content"]["description"] == 'The first video on YouTube. While you wait for Part 2, listen to ' \
                                                    'this great song: https://www.youtube.com/watch?v=zj82_v2R6ts '
    assert json_object["content"]["author"] == 'jawed'
    assert json_object["content"]["channelUrl"] == 'https://www.youtube.com/channel/UC4QobU6STFB0P71PMvOGN5A'
    assert json_object["content"]["title"] == 'Me at the zoo'
    assert "ytimg.com/" in json_object["content"]["thumbnailUrl"]
    assert "googlevideo.com/" in json_object["content"]["streamUrl"]


def test_get_video_lbry():
    """ Test /api/video for Lbry/Odysee. """
    response = client.post(
        "/api/video/",
        json={"id": "@lbry:3f/odysee:7", "platform": "lb"},
    )
    assert response.status_code == 200
    json_object = response.json()
    assert json_object["ready"] == True
    assert json_object["platform"] == 'lb'
    assert json_object["content"]["id"] == '7a416c44a6888d94fe045241bbac055c726332aa'
    assert json_object["content"]["description"] == 'Big thanks to @MH for this ❤️'
    assert json_object["content"]["author"] == 'LBRY'
    assert json_object["content"]["channelUrl"] == 'https://odysee.com/@lbry:3f'
    assert json_object["content"]["title"] == 'Introducing Odysee: A Short Video'
    assert "spee.ch/" in json_object["content"]["thumbnailUrl"]
    assert "lbryplayer.xyz/" in json_object["content"]["streamUrl"]


def test_get_video_bc():
    """ Test /api/video for Bitchute. """
    response = client.post(
        "/api/video/",
        json={"id": "UGlrF9o9b-Q", "platform": "bc"},
    )
    assert response.status_code == 200
    json_object = response.json()
    assert json_object["ready"] == True
    assert json_object["platform"] == 'bc'
    assert json_object["content"]["id"] == 'UGlrF9o9b-Q'
    assert json_object["content"]["author"] == 'BitChute'
    assert json_object["content"]["channelUrl"] == 'https://bitchute.com/channel/bitchute/'
    assert json_object["content"]["title"] == 'This is the first video on #BitChute !'
    assert "bitchute.com/" in json_object["content"]["thumbnailUrl"]
    assert "/UGlrF9o9b-Q.mp4" in json_object["content"]["streamUrl"]
