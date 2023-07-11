
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1 import ImageGrid

measurements = ["TST", "SE"]
folders = ["DeviceOnly", "withHPB"]

fig, axes = plt.subplots(len(measurements), len(folders), figsize=(10, 10))

for i, measurement in enumerate(measurements):
    for j, folder in enumerate(folders):
        file_path = f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/HPB/results/{folder}/Common_Subj_N1_Nodreem/{measurement}_HPB_PSG_BA_N1.png'
        img = mpimg.imread(file_path)
        axes[i, j].imshow(img)
        axes[i, j].set_title(folder.replace("withHPB", "Standard").replace(
            "DeviceOnly", "Device Reported"), fontsize=10, fontweight="bold")
        axes[i, j].axis('off')


for ax in axes.flat:
    ax.axis('off')
    ax.grid(False)
    ax.axis('tight')
    ax.axis('image')

fig.suptitle("Device Reported vs Standard Plots",
             fontsize=16, fontweight="bold")

fig.tight_layout()
plt.savefig('/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/presentations/HPB/plots/DeviceOnly/TST_SE.png', dpi=200)
# plt.show()


measurements = ["WASO", "SOL"]
folders = ["DeviceOnly", "withHPB"]

fig, axes = plt.subplots(len(measurements), len(folders), figsize=(10, 10))

for i, measurement in enumerate(measurements):
    for j, folder in enumerate(folders):
        file_path = f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/HPB/results/{folder}/Common_Subj_N1_Nodreem/{measurement}_HPB_PSG_BA_N1.png'
        img = mpimg.imread(file_path)
        axes[i, j].imshow(img)
        axes[i, j].set_title(folder.replace("withHPB", "Standard").replace(
            "DeviceOnly", "Device Reported"), fontsize=10, fontweight="bold")
        axes[i, j].axis('off')


for ax in axes.flat:
    ax.axis('off')
    ax.grid(False)
    ax.axis('tight')
    ax.axis('image')

fig.suptitle("Device Reported vs Standard Plots",
             fontsize=16, fontweight="bold")

fig.tight_layout()
plt.savefig('/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/presentations/HPB/plots/DeviceOnly/WASO_SOL.png', dpi=200)
# plt.show()


################################################################

measurements = ["Deep", "Light", "REM"]
folders = ["DeviceOnly", "withHPB"]

fig, axes = plt.subplots(len(measurements), len(folders), figsize=(10, 10))

for i, measurement in enumerate(measurements):
    for j, folder in enumerate(folders):
        file_path = f'/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/HPB/results/{folder}/Common_Subj_N1_Nodreem/{measurement}_HPB_PSG_BA_N1.png'
        img = mpimg.imread(file_path)
        axes[i, j].imshow(img)
        axes[i, j].set_title(folder.replace("withHPB", "Standard").replace(
            "DeviceOnly", "Device Reported"), fontsize=10, fontweight="bold")
        axes[i, j].axis('off')


for ax in axes.flat:
    ax.axis('off')
    ax.grid(False)
    ax.axis('tight')
    ax.axis('image')

fig.suptitle("Device Reported vs Standard Plots",
             fontsize=16, fontweight="bold")

fig.tight_layout()
plt.savefig('/Volumes/CSC5/SleepCognitionLab/Tera2b/Experiments/OuraValidation/Oura3/analysis/DeZambotti/presentations/HPB/plots/DeviceOnly/stages.png', dpi=200)
# plt.show()
