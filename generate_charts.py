import matplotlib.pyplot as plt

# Set consistent styling
plt.style.use('ggplot')
PRIMARY_COLOR = '#0f2b48'
ACCENT_COLOR = '#0284c7'

def generate_pie_chart(filename="booking_pie_chart.png"):
    # Data for Pie Chart: Booking Distribution by Sport
    sports = ['Box Cricket', 'Football Turf', 'Tennis Court', 'Badminton']
    percentages = [45, 30, 15, 10]
    colors = ['#0f2b48', '#0284c7', '#38bdf8', '#cbd5e1']

    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    wedges, texts, autotexts = ax.pie(
        percentages, 
        labels=sports, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors,
        textprops=dict(color="#0f172a", weight="bold"),
        wedgeprops=dict(width=0.6, edgecolor='white', linewidth=2) # Donut chart style
    )

    for autotext in autotexts:
        autotext.set_color('white')

    ax.set_title("Booking Share by Sport Type", fontsize=14, weight='bold', color=PRIMARY_COLOR, pad=20)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    print(f"✅ Generated Pie Chart image successfully as '{filename}'")

def generate_bar_graph(filename="peak_hours_bar_graph.png"):
    # Data for Bar Graph: Hourly Occupancy Trend
    time_slots = ['6 AM-9 AM', '9 AM-12 PM', '12 PM-3 PM', '3 PM-6 PM', '6 PM-9 PM', '9 PM-12 AM']
    bookings_count = [35, 15, 10, 25, 50, 40]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    bars = ax.bar(time_slots, bookings_count, color=ACCENT_COLOR, edgecolor=PRIMARY_COLOR, linewidth=1.2, width=0.55)

    # Highlight Peak Hours with a darker shade
    bars[4].set_color(PRIMARY_COLOR)

    # Adding values above bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f'{yval}', ha='center', va='bottom', weight='bold', color='#0f172a')

    ax.set_title("Booking Demand Across Time Slots (Peak Hours)", fontsize=14, weight='bold', color=PRIMARY_COLOR, pad=15)
    ax.set_xlabel("Time Slots", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_ylabel("Total Slot Bookings", fontsize=11, weight='bold', color=PRIMARY_COLOR)
    ax.set_ylim(0, 60)

    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    print(f"✅ Generated Bar Graph image successfully as '{filename}'")

if __name__ == "__main__":
    generate_pie_chart()
    generate_bar_graph()