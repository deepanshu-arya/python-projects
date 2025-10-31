from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime

# ============================================================
# 🗃️ Database Configuration
# ============================================================
DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# 📝 Database Model
# ============================================================
class Blog(Base):
    """SQLAlchemy model representing a blog post."""
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        String, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nullable=False
    )


# Create all tables
Base.metadata.create_all(bind=engine)


# ============================================================
# 🧩 Pydantic Schemas
# ============================================================
class BlogCreate(BaseModel):
    title: str = Field(..., example="My First Blog", min_length=3, max_length=100)
    author: str = Field(..., example="John Doe", min_length=2)
    content: str = Field(..., example="This is an example of a detailed blog post.")


class BlogUpdate(BaseModel):
    title: str | None = Field(None, example="Updated Blog Title")
    author: str | None = Field(None, example="Updated Author Name")
    content: str | None = Field(None, example="Updated content for the blog post.")


# ============================================================
# ⚙️ Utility - Database Dependency
# ============================================================
def get_db():
    """Create and close a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 🚀 FastAPI App Initialization
# ============================================================
app = FastAPI(
    title="BlogSphere CMS API",
    version="1.2.0",
    description="A modern and efficient Content Management API for creating, updating, and managing blog posts using FastAPI.",
)


# ============================================================
# 🧠 Helper Functions
# ============================================================
def log_action(action: str):
    """Log timestamped actions for better debugging and tracking."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - {action}")


def get_blog_or_404(blog_id: int, db: Session) -> Blog:
    """Helper function to fetch a blog post by ID or raise a 404 error."""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog post with ID {blog_id} not found."
        )
    return blog


# ============================================================
# 🏠 Root Route
# ============================================================
@app.get("/", tags=["Home"])
def home():
    """Home route for API introduction."""
    log_action("Home route accessed.")
    return {"message": "Welcome to BlogSphere CMS API!"}


# ============================================================
# 📝 Create Blog Post
# ============================================================
@app.post("/blogs/", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["Blogs"])
def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    """Create a new blog post."""
    new_blog = Blog(title=blog.title, author=blog.author, content=blog.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    log_action(f"Created new blog: '{new_blog.title}' by {new_blog.author}")
    return {"message": "✅ Blog post created successfully", "blog_id": new_blog.id}


# ============================================================
# 📚 Get All Blog Posts
# ============================================================
@app.get("/blogs/", response_model=list[dict], status_code=status.HTTP_200_OK, tags=["Blogs"])
def get_all_blogs(db: Session = Depends(get_db)):
    """Retrieve all blog posts."""
    blogs = db.query(Blog).all()
    log_action("Fetched all blog posts.")

    return [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "content": b.content,
            "created_at": b.created_at,
        }
        for b in blogs
    ]


# ============================================================
# 🔍 Get Blog by ID
# ============================================================
@app.get("/blogs/{blog_id}", response_model=dict, status_code=status.HTTP_200_OK, tags=["Blogs"])
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    """Retrieve a single blog post by ID."""
    blog = get_blog_or_404(blog_id, db)
    log_action(f"Viewed blog post ID: {blog_id}")
    return {
        "id": blog.id,
        "title": blog.title,
        "author": blog.author,
        "content": blog.content,
        "created_at": blog.created_at,
    }


# ============================================================
# ✏️ Update Blog Post
# ============================================================
@app.put("/blogs/{blog_id}", response_model=dict, status_code=status.HTTP_200_OK, tags=["Blogs"])
def update_blog(blog_id: int, blog_update: BlogUpdate, db: Session = Depends(get_db)):
    """Update an existing blog post."""
    blog = get_blog_or_404(blog_id, db)

    # Apply updates dynamically
    if blog_update.title is not None:
        blog.title = blog_update.title
    if blog_update.author is not None:
        blog.author = blog_update.author
    if blog_update.content is not None:
        blog.content = blog_update.content

    db.commit()
    db.refresh(blog)

    log_action(f"Updated blog post ID: {blog_id}")
    return {
        "message": "✅ Blog post updated successfully",
        "updated_blog": {
            "id": blog.id,
            "title": blog.title,
            "author": blog.author,
            "content": blog.content,
            "created_at": blog.created_at,
        },
    }


# ============================================================
# ❌ Delete Blog Post
# ============================================================
@app.delete("/blogs/{blog_id}", response_model=dict, status_code=status.HTTP_200_OK, tags=["Blogs"])
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    """Delete a blog post by ID."""
    blog = get_blog_or_404(blog_id, db)
    db.delete(blog)
    db.commit()

    log_action(f"Deleted blog post ID: {blog_id}")
    return {"message": f"🗑️ Blog post ID {blog_id} deleted successfully"}
