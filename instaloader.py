import instaloader.instaloader
import instaloader

L = instaloader.instaloader()

profile = instaloader.Profile.from_username(L.context, "virat.kohli")

print("Username:", profile.username)
print("Full Name:", profile.full_name)
print("Biography:", profile.biography)
print("Followers:", profile.followers)

posts = []
for post in profile.get_posts():
    posts.append({
        "caption": post.caption,
        "image_url": post.url
    })
    if len(posts) == 5:
        break

print(posts)
