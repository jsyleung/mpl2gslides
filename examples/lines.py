import mpl2gslides as ms
import matplotlib.pyplot as plt
import os

PRESENTATION_TITLE = "My Vector Plot Presentation"

if not os.getenv("GSLIDES_CREDENTIALS"):
    raise EnvironmentError("Please set the GSLIDES_CREDENTIALS environment variable to point to your Google API credentials file.")

# Step 1: Authorize and get the Slides API service
service = ms.get_slides_service()

# Step 2: Get (or create) the presentation
presentation_id = ms.get_presentation(service, title=PRESENTATION_TITLE)

# Step 3: Add a slide
slide_id = ms.add_blank_slide(service, presentation_id)

# Step 4: Create a matplotlib plot and extract requests
fig, ax = plt.subplots()
ax.plot([0, 1, 2, 3, 4], [0, 1, 0.4, 0.7, 0.2], color="C0")
ax.plot([0, 1, 2, 3, 4], [1, 0, 0.3, 0.3, 0.9], color="C1")
requests = ms.plot_to_api_requests(ax, slide_id=slide_id)
plt.close(fig)

# Step 5: Send the requests to Google Slides
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={"requests": requests}
).execute()

# Step 6: Print the presentation URL
print(f"Plot inserted to https://docs.google.com/presentation/d/{presentation_id}/edit")
