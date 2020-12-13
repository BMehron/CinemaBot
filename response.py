import bot_language
import aiohttp
import json
from bot_language import TMDB, API_KEY, LANGUAGE


class Response:
    def __init__(self) -> None:
        self.description = ""
        self.photo = None  # poster
        self.title = ""

    async def response_name_query(self, session: aiohttp.ClientSession, query: str) -> str:
        Response.__init__(self)
        async with session.get(
                f"{TMDB}search/movie?api_key={API_KEY}&query={query}&language={LANGUAGE}") as result:
            response = json.loads(await result.text())
            if len(response['results']) == 0:
                return bot_language.NOT_FOUND_MSG.format(query)
            output_text = bot_language.FIND_MSG.format(query)
            for movie in response['results']:
                async with session.get(
                        f"{TMDB}movie/{movie['id']}?api_key={API_KEY}&append_to_response=videos&language={LANGUAGE}") \
                        as req:
                    info = json.loads(await req.text())
                    title = info['original_title']
                    if len(info['release_date']) == 0:
                        continue
                    year = info['release_date'][:4]
                    if len(info['production_countries']):
                        country = info['production_countries'][0]['name']
                    else:
                        continue
                    if len(info['genres']):
                        genre = info['genres'][0]['name']
                    else:
                        continue

                    output_text += "● {} [{},\t {},\t️ {};\t/i{}]\n".format(title, year, country, genre,
                                                                            movie['id'])
            return output_text

    async def response_id_query(self, session: aiohttp.ClientSession, film_id) -> None:
        async with session.get(
                f"{TMDB}movie/{film_id}?api_key={API_KEY}&append_to_response=videos&language={LANGUAGE}") as result:
            movie = json.loads(await result.text())
            title = movie['original_title']
            self.title = title
            genres = []
            for genre in movie['genres']:
                genres.append(genre['name'])
            countries = []
            for country in movie['production_countries']:
                countries.append(country['name'])
            self.description = title + "\n[📅: {}, 🌍 {}, ⭐️{}] \n".format(movie['release_date'],
                                                                           countries[0], movie['vote_average'])
            # Tagline
            if len(movie['tagline']) > 0:
                self.description += "📢 {}\n".format(movie['tagline'])
            # Duration
            if movie['runtime'] is not None:
                self.description += "⏱️ {} мин.\n".format(movie['runtime'])
            # Genres
            if len(genres) > 0:
                genres = ", ".join(genres)
                self.description += "🎭 {}\n".format(genres)
            if len(movie['overview']):
                self.description += "📄 {}\n".format(movie['overview'])
            if len(movie['videos']['results']) > 0:
                trailer_key = movie['videos']['results'][0]['key']
                self.description += "🎥 Посмотреть [трейлер на русском]({}).\n".format(
                    "https://www.youtube.com/watch?v={}".format(trailer_key))
            else:
                async with session.get(
                        f"{TMDB}movie/{film_id}?api_key={API_KEY}&append_to_response=videos") as req:
                    movie = json.loads(await req.text())
                    if len(movie['videos']['results']) > 0:
                        trailer_key = movie['videos']['results'][0]['key']
                        self.description += "🎥 Посмотреть [трейлер на английском]({}).\n".format(
                            "https://www.youtube.com/watch?v={}".format(trailer_key))

            if len(movie['poster_path']) > 0:
                self.photo = "https://image.tmdb.org/t/p/original/{}".format(movie['poster_path'])


if __name__ == '__main__':
    pass
