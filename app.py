from flask import Flask,render_template,request
import pickle
import numpy as np
import pandas as pd

popular_df = pd.read_pickle('popular.pkl')
pt = pd.read_pickle('pt.pkl')
books = pd.read_pickle('books.pkl')
similarity_scores = pd.read_pickle('similarity_scores.pkl')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    indices = np.where(pt.index == user_input)[0]
    if len(indices) == 0:
        # user input not found in pt.index, handle gracefully
        return render_template('recommend.html', data=[], message="Book not found. Please try another title or give exact title.")
    index = indices[0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)

@app.route('/book/<book_title>')
def book_detail(book_title):
    indices = np.where(pt.index == book_title)[0]
    if len(indices) == 0:
        return render_template('book_detail.html', message="Book not found. Please enter the exact book title.", data=[])
    index = indices[0]
    # Get book details
    temp_df = books[books['Book-Title'] == book_title].drop_duplicates('Book-Title')
    if temp_df.empty:
        return render_template('book_detail.html', message="Book details not found.", data=[])
    # Get votes and rating from popular_df
    pop_df = popular_df[popular_df['Book-Title'] == book_title]
    votes = pop_df['num_ratings'].values[0] if not pop_df.empty else None
    rating = pop_df['avg_rating'].values[0] if not pop_df.empty else None

    book_info = {
        'title': temp_df['Book-Title'].values[0],
        'author': temp_df['Book-Author'].values[0],
        'image': temp_df['Image-URL-M'].values[0],
        'votes': votes,
        'rating': rating
    }
    # Get similar books
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:9]
    recommendations = []
    for i in similar_items:
        rec_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
        if not rec_df.empty:
            pop_df = popular_df[popular_df['Book-Title'] == rec_df['Book-Title'].values[0]]
            votes = pop_df['num_ratings'].values[0] if not pop_df.empty else None
            rating = pop_df['avg_rating'].values[0] if not pop_df.empty else None
            recommendations.append({
                'title': rec_df['Book-Title'].values[0],
                'author': rec_df['Book-Author'].values[0],
                'image': rec_df['Image-URL-M'].values[0],
                'votes': votes,
                'rating': rating
            })
    return render_template('book_detail.html', book=book_info, recommendations=recommendations)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
