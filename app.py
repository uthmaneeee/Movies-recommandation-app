import streamlit as st 
import streamlit.components.v1 as stc
import pickle
import requests
import pandas as pd
import requests
import json
from datetime import datetime

import matplotlib.pyplot as plt
TMDB_API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzZWU0NTQ3MThlMzlhZDk2MWJkZTFmYzViY2MxMGIxZSIsInN1YiI6IjY1NTk0ZWUyMDgxNmM3MDExYTBkOWYxYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.DrjT_4bZ-O1GbPxXDy2sjedlEy6wMt3yQaq8BUYaIds'  # Replace with your actual API key



HTML_BANNER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>

<div style="background-color: #464e5f; height: 80%; padding: 10px; border-radius: 10px; box-shadow: 0 4px 8px rgba(255, 255, 255, 0.2); display: flex; flex-direction: column; justify-content: space-between;">
    <div style="text-align: center;">
        <img src="https://img.freepik.com/free-psd/ready-cinema-with-popcorn-drinks-3d-illustration_1419-2557.jpg?w=740&t=st=1701089326~exp=1701089926~hmac=5d016ecd3402711faa8a24c858990a52bad2d5c2a8cc3c95e3f70b93516a6ee7" alt="Banner Image" style="height: 8%; object-fit: cover; border-radius: 6px; margin-bottom: 8px; animation: rotate 10s linear infinite;">
        <h1 style="color: #fff; text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.5);">Movie Directory App</h1>
    </div>
    <div style="text-align: center;">
        <h1 style="color: #fff; text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.5);">Your Text Goes Here</h1>
    </div>
</div>

<style>
    @keyframes rotate {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }
</style>

</body>
</html>

"""

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie,movies,similarity):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names,recommended_movie_posters
def extract_genres(genres):
			ls = []
			genre_list = eval(genres)
			for obj in genre_list:
				if 'name' in obj:
					ls.append(obj['name'])
			return ls
def main():
	"""Movie Recommender System App"""
	
	menu = ["Home","Search By release date","Search By genres","Recommendation","About"]
	choice = st.sidebar.selectbox("Menu",menu)
	stc.html(HTML_BANNER,height=200)

	df = pd.read_csv("movies_metadata.csv")
	#cleaning data
	df = df.drop_duplicates()
	df = df.reset_index(drop=True)
	# if a genre has less than 10 movies, we will remove it from the DataFrame
	# unique values of genre (more than 10 movies)
	df['genres_list'] = df['genres'].apply(lambda genres: extract_genres(genres))
	exploded_df = df.explode('genres_list')
	genre_counts = exploded_df['genres_list'].value_counts()
	unique_genres = genre_counts[genre_counts > 10].index.tolist()
	df = df[df['genres_list'].apply(lambda genres: any(genre in unique_genres for genre in genres))]

	if choice == 'Home':
		st.subheader("Home")
		movies_original_title_list = df['original_title'].tolist()

		movie_choice = st.selectbox("Choose a movie",movies_original_title_list)
		st.subheader("Let's check some useful informations about this movies :)")
		movie_id =  df[df['original_title'] == movie_choice]['id'].values[0]
		# Endpoint for retrieving movie details, including images
		url = f"https://api.themoviedb.org/3/movie/{movie_id}/images"
		headers = {
				"Accept": "application/json",
				"Authorization": f"Bearer {TMDB_API_KEY}"
			}

		response = requests.get(url, headers=headers)
		if response.status_code == 200:
				movie_img = response.json()
				#st.write(movie_img)
				images = movie_img['backdrops']
				for image in images:
					poster_path = f"https://image.tmdb.org/t/p/original{image['file_path']}"
					#st.image(image_url, caption=image['file_path'], use_column_width=True)
					#st.image(image_url, use_column_width=True)
					
			
		else:
			st.error(f"Error: {response.status_code}, {response.text}")

		original_title = df[df['original_title']== movie_choice]['original_title'].values
		genre_ = df[df['original_title']== movie_choice]['genres']
		for genre in genre_:
				# Replace single quotes with double quotes
				genre_json = genre.replace("'", "\"")
				
				try:
					# Load the corrected JSON string
					genres_data = json.loads(genre_json)
					genre_names = [genre['name'] for genre in genres_data]
					print(genre_names)
				except json.JSONDecodeError as e:
					print(f"Error decoding JSON: {e}")



		# Layout the columns for the home page
		c1,c2,c3 = st.columns([1,2,1])

		with c1:
			with st.expander ("original_title"):
				st.success(original_title[0])


		with c2:
			with st.expander ("Poster"):
				st.image(poster_path,width=200)


		with c3:
			with st.expander ("Genres"):
				for g in genre_names:
					st.info(g)


	elif choice == "Search By release date":
		st.subheader("Search Movies ")
		with st.expander("Search By release_date"):
			df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

			movie_release_date = st.number_input("Release Year", 1995, 2020)
			# Filter DataFrame based on the release year
			df_for_release_date = df[df['release_date'].dt.year == movie_release_date].head(10)
	
			for index, row in df_for_release_date.iterrows():
						
						movie_id = row['id']
						original_title = row['original_title']
						# Endpoint for retrieving movie details, including images
						url = f"https://api.themoviedb.org/3/movie/{movie_id}/images"
						headers = {
							"Accept": "application/json",
							"Authorization": f"Bearer {TMDB_API_KEY}"
						}

						response = requests.get(url, headers=headers)

						st.title(original_title)
						#st.write(response.status_code)

						if response.status_code == 200:
							movie_img = response.json()
							#st.write(movie_img)
							try :
								images = movie_img['backdrops']
								image=images[0]
								poster_path = f"https://image.tmdb.org/t/p/original{image['file_path']}"
								st.image(poster_path, width=100)
							except:
								st.write("No image available")
	elif choice == "Search By genres":

		st.subheader("Search Movies ")

		# Convert release_date column to datetime
		df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
		df['Year'] = df['release_date'].dt.year
		df['genres_list'] = df['genres'].apply(lambda genres: extract_genres(genres))

		# Get all unique values for genre
		unique_genres = set([genre for value in df['genres_list'] for genre in value])
		with st.expander("Search By Genres"):
				selected_genre = st.selectbox("Select Genre", ['Action'] + list(unique_genres))

				# Filter DataFrame based on the selected genre
				filtered_df = df[df['genres_list'].apply(lambda genres: selected_genre in genres if selected_genre != 'Any' else True)]

				# Plot the number of movies per year for the selected genre
				plt.figure(figsize=(10, 6))
				plt.bar(filtered_df['Year'].value_counts().sort_index().index,
						filtered_df['Year'].value_counts().sort_index().values,
						color='skyblue')
				plt.xlabel('Year')
				plt.ylabel('Number of Movies')
				plt.title(f'Number of Movies per Year for Genre: {selected_genre}')
				st.set_option('deprecation.showPyplotGlobalUse', False)
				st.pyplot()
				#st.write('Example of movies')
				text_to_display = "Examples of movies"
				st.markdown(f"<span style='font-size: 40px'>{text_to_display}</span>", unsafe_allow_html=True)

				# Display movie details
				for index, row in filtered_df.head(10).iterrows():
					movie_id = row['id']
					original_title = row['original_title']
					# Endpoint for retrieving movie details, including images
					url = f"https://api.themoviedb.org/3/movie/{movie_id}/images"
					headers = {
						"Accept": "application/json",
						"Authorization": f"Bearer {TMDB_API_KEY}"
					}

					response = requests.get(url, headers=headers)

					st.title(original_title)
					if response.status_code == 200:
							movie_img = response.json()
							#st.write(movie_img)
							try :
								images = movie_img['backdrops']
								image=images[0]
								poster_path = f"https://image.tmdb.org/t/p/original{image['file_path']}"
								st.image(poster_path, width=100)
							except:
								st.write("No image available")

						

					

	elif choice == "Recommendation":
		st.header('Movie Recommender System')
		movies = pickle.load(open('model/movie_list.pkl','rb'))
		similarity = pickle.load(open('model/similarity.pkl','rb'))

		movie_list = movies['title'].values
		selected_movie = st.selectbox(
			"Type or select a movie from the dropdown",
			movie_list
		)

		if st.button('Show Recommendation'):
			recommended_movie_names,recommended_movie_posters = recommend(selected_movie,movies,similarity)
			col1, col2, col3, col4, col5 = st.columns(5)
			with col1:
				st.text(recommended_movie_names[0])
				st.image(recommended_movie_posters[0])
			with col2:
				st.text(recommended_movie_names[1])
				st.image(recommended_movie_posters[1])

			with col3:
				st.text(recommended_movie_names[2])
				st.image(recommended_movie_posters[2])
			with col4:
				st.text(recommended_movie_names[3])
				st.image(recommended_movie_posters[3])
			with col5:
				st.text(recommended_movie_names[4])
				st.image(recommended_movie_posters[4])



	

	else:
		st.subheader("About")
		st.text("Built with Streamlit")
		st.text("Othmane Nabgouri , Hugo Monchal @M2-Miashs")



if __name__ == '__main__':
	main()



