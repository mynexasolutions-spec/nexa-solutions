from flask import Blueprint, render_template, abort, request
from app.models.blog import BlogPost, Category

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/blog')
def list_posts():
    search_query = request.args.get('q') # Get the text from the search input
    # Look for the ?category=... in the URL
    category_name = request.args.get('category')
    categories = Category.query.all()

    # Start with all published posts
    query = BlogPost.query.filter_by(is_published=True)

    # If user searched for something, filter by title or summary
    if search_query:
        query = query.filter(
            BlogPost.title.ilike(f'%{search_query}%') | 
            BlogPost.summary.ilike(f'%{search_query}%')
        )
    
    if category_name:
        # Filter posts by the category name clicked
        posts = BlogPost.query.join(Category).filter(Category.name == category_name).all()
    else:
        # Show everything if no category is selected
        posts = BlogPost.query.all()
        
    return render_template('blog/blog_list.html', posts=posts, categories=categories)

@blog_bp.route('/blog/<slug>')
def detail(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    # We also fetch all categories so the navbar/footer stay consistent
    categories = Category.query.all()
    return render_template('blog/blog_detail.html', post=post, categories=categories)

@blog_bp.route('/blog/category/<string:category_name>')
def list_by_category(category_name):
    # 1. Find the category by name
    category = Category.query.filter_by(name=category_name).first_or_404()
    
    # 2. Get all published posts in that category
    posts = BlogPost.query.filter_by(category_id=category.id, is_published=True).all()
    
    # 3. Get all categories for the sidebar/filter menu
    categories = Category.query.all()
    
    return render_template('blog/blog_list.html', posts=posts, categories=categories)

