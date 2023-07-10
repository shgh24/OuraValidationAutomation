import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1 import ImageGrid


measurements = ["TST", "WASO", "SOL", "SE"]
for measurement in measurements:

    # Define the file paths to the plots
    file_paths = [
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/results/withHPB/Common_Subj_N1_Nodreem/{measurement}_Oura3_PSG_BA_N1_L_2023_06_13.png',
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/FB/results/withHPB/Common_Subj_N1_Nodreem/{measurement}_FB_PSG_BA_N1.png',
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/HPB/results/withHPB/Common_Subj_N1_Nodreem/{measurement}_HPB_PSG_BA_N1.png',
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Acti/Results/withHPB/Common_Subj_N1_Nodreem/{measurement}_Acti_PSG_BA_N1.png'
    ]

    # Define the folder names corresponding to the plots
    folder_names = ["Oura3", "FB", "HPB", "Acti"]

    # Create an empty list to store the plot images
    plot_images = []

    # Load the plot images
    for file_path in file_paths:
        img = mpimg.imread(file_path)
        plot_images.append(img)

    # Set up the figure with the desired size
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    # Iterate over the axes and plot the images
    for ax, img, folder_name in zip(axes.ravel(), plot_images, folder_names):
        ax.imshow(img)
        ax.set_title(folder_name, fontsize=20,
                     fontname="sans-serif", fontweight="bold")
        ax.axis('off')  # Turn off the axis

    # Set the title for the combined plot
    fig.suptitle("Combined Plots")

    # Adjust the spacing between subplots
    fig.tight_layout()

    # Display the combined plot

    fig.savefig(
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/presentations/HPB/plots/{measurement}.png', dpi=200)
    print('done')
    # plt.show()


measurements = ["Deep", "Light", "REM"]
for measurement in measurements:

    # Define the file paths to the plots
    file_paths = [
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/Oura3/results/withHPB/Common_Subj_N1_Nodreem/{measurement}_Oura3_PSG_BA_N1_L_2023_06_13.png',
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/FB/results/withHPB/Common_Subj_N1_Nodreem/{measurement}_FB_PSG_BA_N1.png',
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/HPB/results/withHPB/Common_Subj_N1_Nodreem/{measurement}_HPB_PSG_BA_N1.png'

    ]

    # Define the folder names corresponding to the plots
    folder_names = ["Oura3", "FB", "HPB"]

    # Create an empty list to store the plot images
    plot_images = []

    # Load the plot images
    for file_path in file_paths:
        img = mpimg.imread(file_path)
        plot_images.append(img)

    # Set up the figure with the desired size
    fig, axes = plt.subplots(1, 3, figsize=(10, 10))

    # Iterate over the axes and plot the images
    for ax, img, folder_name in zip(axes.ravel(), plot_images, folder_names):
        ax.imshow(img)
        ax.set_title(folder_name, fontsize=20,
                     fontname="sans-serif", fontweight="bold")
        ax.axis('off')  # Turn off the axis

    # Set the title for the combined plot
    fig.suptitle("Combined Plots")

    # Adjust the spacing between subplots
    fig.tight_layout()

    # Display the combined plot

    fig.savefig(
        f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/presentations/HPB/plots/{measurement}.png', dpi=200)
    print('done')
    # plt.show()
