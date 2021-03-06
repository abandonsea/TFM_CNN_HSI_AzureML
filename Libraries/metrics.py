###############################################################
# Alberto Martín Pérez - 2021
# This script has been developed by Guillermo Vázquez Valle. 
# Some modifications have been done.
#--------------------------------------------------------------
# This script is used to extract metrics from a prediction.
# It is also used to generate classification maps.
###############################################################

import numpy as np					# Import numpy
import matplotlib.pyplot as plt		# Import matplotlib pyplot

#*##########################
#*#### DEFINED METHODS #####
#*
def get_metrics(true_labels, pred_labels, num_clases):
	"""
    Takes true and predicted labels to generate a confusion matrix and extract overall accuracy,
    accuracy, sensitivity, specificity and precission metrics for every input class.

    Inputs
    ----------
    - 'true_labels':	Numpy array with original true labels
    - 'pred_labels':	Numpy array with predicted labels
    - 'num_clases':		Integer with the number of unique classes

	Outputs
    ----------
	- Python dictionary with the following key and values:
		- 'OACC': Overall accuracy value
		- 'SEN': Sensivity python list with each class sensitivity value
		- 'SPE': Specificity python list with each class specificity value
		- 'ACC': Accuracy python list with each class accuracy value
		- 'PRECISION': Precission python list with each class precission value
		- 'CON_MAT': Confusion matrix numpy array
    """

    #*################
    #* ERROR CHECKER
    #*
    # Check if 'true_labels' and 'pred_labels' are numpy arrays
	if not isinstance(true_labels, np.ndarray):
		raise TypeError("Expected numpy array as input. Received instead variable 'true_labels' of type: ", str(type(true_labels)) )
	if not isinstance(pred_labels, np.ndarray):
		raise TypeError("Expected numpy array as input. Received instead variable 'pred_labels' of type: ", str(type(pred_labels)) )

	# Check if 'true_labels' and 'pred_labels' have the same shape
	if not (true_labels.shape == pred_labels.shape):
		raise RuntimeError("Expected 'labels' and 'pred_labels' to have the same shape. Received true_labels.shape = ", str(true_labels.shape), " and pred_labels.shape = ", str(pred_labels.shape))

	# Check if 'true_labels' and 'pred_labels' are numpy column vectors
	if not (true_labels.shape[1] == 1 and pred_labels.shape[1] == 1):
		raise RuntimeError("Expected 'true_labels' and 'pred_labels' to be column vectors of shape (N, 1). Received true_labels.shape = ", str(true_labels.shape), " and pred_labels.shape = ", str(pred_labels.shape))
    #*    
    #* END OF ERROR CHECKER ###
    #*#########################

	# Create empty confusion matrix with dimensions 'num_clases'
	confusion_mx = np.zeros([num_clases, num_clases], dtype='int')

    #*##################################################
    #* FOR LOOP ITERATES OVER ALL INPUT LABELS
    #* ON EACH ITERATION WE ADD 1 TO THE CORRESPONDING
	#* CONFUSION MATRIX INDEX.
    #*
	for i in range(true_labels.shape[0]):
    	# We substract 1 to the index since numpy true_labels[i] or pred_labels[i] contain integers > 0
		# Remember that confusion_mx is a numpy array and index starts at 0.
		confusion_mx[true_labels[i]-1, pred_labels[i]-1] += 1
	#*
    #* END FOR LOOP
    #*##############

	# Call private method '__class_metrics()' to obtain sensivity, specifity, accuracy and precission 
	# vectors where each element corresponds to the metric obtained in each class.
	sensivity, specifity, accuracy, precission = __class_metrics(confusion_mx)

	# Compute the overall accuracy
	oac = np.sum(np.diag(confusion_mx)) / np.sum(confusion_mx)

	return {'OACC':oac, 'SEN':sensivity, 'SPE':specifity, 'ACC':accuracy, 'PRECISION':precission, 'CON_MAT': confusion_mx}

def __class_metrics(confusion_mx):
	"""
    (Private method) Computes the sensitivity, specificity, accuracy and precission metrics
    for every class available in the input confusion matrix.

    Inputs
    ----------
    - 'confusion_mx': Confusion matrix generated in 'get_metrics()' method.

	Outputs
    ----------
	- 'sensivity':	Sensivity python list with each class sensitivity value
	- 'specifity':	Specificity python list with each class specificity value
	- 'accuracy':	Accuracy python list with each class accuracy value
	- 'precission':	Precission python list with each class precission value
    """

	# Create empty Python list for evert metric
	sensivity = [] 
	specifity = []
	accuracy = []
	precission = []

	epsilon = 10e-8
	
	#*####################################################
    #* FOR LOOP ITERATES OVER THE INPUT CONFUSION MATRIX
    #* ON EACH ITERATION WE COMPUTE THE TP, TN, FP and FN
	#* FOR THE CORRESPONDING LABEL. THEN WE COMPUTE THE
	#* SEN, SPE, ACC and PRE METRICS FOR THAT LABEL.
    #*
	for i in range(confusion_mx.shape[0]):

		tp = confusion_mx[i,i]
		fn = np.sum(confusion_mx[i,:])-tp
		fp = np.sum(confusion_mx[:,i])-tp
		tn = np.sum(confusion_mx)-tp-fp-fn

		sensivity.append(tp/(tp+fn+epsilon))
		specifity.append(tn/(tn+fp+epsilon))
		accuracy.append((tn+tp)/(tn+tp+fn+fp+epsilon))
		precission.append(tp/(tp+fp+epsilon))
	#*
    #* END FOR LOOP
    #*##############

	return sensivity, specifity, accuracy, precission

def get_classification_map(pred_labels, true_labels=None, coordenates=None, dims=None, title= None, plot = True, save_plot = False, save_path = None, plot_gt = True, padding = 0, dpi=120):
	"""
	Generates classification maps from the input labels.
	It can generate:
	- Single plot with the predicted classification map.
	- A subplot with the original ground-truth and the predicted ground-truth.
	- Single plot with the predicted classification map from an entire cube.

    Inputs
    ----------
    - 'pred_labels':	Numpy array with predicted labels
    - 'true_labels':	Numpy array with original true labels
	- 'coordenates':	Numpy array with the coordenates of each labeled pixel of the ground truth map
    - 'dims':			Python list containing the dimensions of the classified ground truth map
    - 'title':			String to set the title of the subplot
    - 'plot':			Boolean flag to indicate whether or not to show on screen the plot
    - 'save_plot':		Boolean flag to indicate whether or not to save the plot
    - 'save_path':		String variable containing the path to save the subplot
	- 'plot_gt':		Boolean flag to indicate whether or not
	- 'padding':		Integer. Value used to pad images to generate the batches. Used to delete empty rows and columns for the bottom and right.
	- 'dpi':			Integer. DPI value when saving the pyplot figures.
    
	Outputs
    ----------
	- 'preds_color':	PyPlot figure with the predicted map with colors for every label4Class.
	- 'gt_color':		PyPlot figure with the ground-truth map with colors for every label4Class.
	"""
	#*################
    #* ERROR CHECKER
    #*
    # Check if 'true_labels' and 'pred_labels' are numpy arrays
	if not isinstance(pred_labels, np.ndarray):
		raise TypeError("Expected numpy array as input. Received instead variable 'pred_labels' of type: ", str(type(pred_labels)) )
	
	# Enter this if statement if we want to plot the ground-truth as well
	if(plot_gt):
		if not isinstance(true_labels, np.ndarray):
			raise TypeError("Expected numpy array as input. Received instead variable 'true_labels' of type: ", str(type(true_labels)) )

		# Check if 'true_labels' and 'pred_labels' have the same shape
		if not (true_labels.shape == pred_labels.shape):
			raise RuntimeError("Expected 'labels' and 'pred_labels' to have the same shape. Received true_labels.shape = ", str(true_labels.shape), " and pred_labels.shape = ", str(pred_labels.shape))

		# Check if 'true_labels' and 'pred_labels' are numpy column vectors
		if not (true_labels.shape[1] == 1 and pred_labels.shape[1] == 1):
			raise RuntimeError("Expected 'true_labels' and 'pred_labels' to be column vectors of shape (N, 1). Received true_labels.shape = ", str(true_labels.shape), " and pred_labels.shape = ", str(pred_labels.shape))
    #*    
    #* END OF ERROR CHECKER ###
    #*#########################

	# Create empty variables (in case we return a figure that has not been created)
	fig_predMap = None
	fig_GTs = None

	# Extract X and Y coordenates independently. 
	# Extracting 1 column results in a 1D array, therefore we need to reshape 
	# to have a (N, 1) shape and index labels to each coordenate properly.
	# Otherwise, we would encounter the following error:
	#	ValueError: shape mismatch: value array of shape (N,1)  could not be broadcast to indexing result of shape (N,)
	x = coordenates[:, 0].reshape((len(coordenates), 1))
	y = coordenates[:, -1].reshape((len(coordenates), 1))

    # Generate empty arrays with same dimensions as the ground truth map.
	pred_raw_map = np.zeros((dims[0], dims[1]))

	# Update the raw maps with the corresponding labels for every coordenate
	pred_raw_map[x, y] = pred_labels

	# Convert the raw map with labels to color maps
	preds_color =  _convert2color(pred_raw_map)

	# Delete added padding to the right and bottom
	preds_color = preds_color[2*padding:preds_color.shape[0]-2*padding, 2*padding:preds_color.shape[1]-2*padding]

	# Create plot with figure to be returned for Azure
	fig_predMap = plt.figure(dpi=dpi)
	plt.title(title)
	plt.imshow(preds_color)
	plt.axis('off')
	# Plot prediction map
	if plot:
		plt.show()

	# Do the same with the ground truth labels in case we want to plot it
	if(plot_gt):
    	# Generate empty arrays with same dimensions as the ground truth map.
		gt_raw_map = np.zeros((dims[0], dims[1]))

		# Update the raw maps with the corresponding labels for every coordenate
		gt_raw_map[x, y] = true_labels

		# Convert the raw map with labels to color maps
		gt_color = _convert2color(gt_raw_map)

    	# Delete added padding to the right and bottom
		gt_color = gt_color[2*padding:gt_color.shape[0]-2*padding, 2*padding:gt_color.shape[1]-2*padding]
		
		# Create plot with figure to be returned for Azure
		fig_GTs = plt.figure(dpi=dpi)
		fig_GTs.add_subplot(1, 2, 1)
		plt.imshow(preds_color)
		plt.title("Prediction")
		plt.axis('off')
		fig_GTs.add_subplot(1, 2, 2)
		plt.imshow(gt_color)
		plt.title("Ground truth")
		plt.axis('off')
		# Plot the prediction map and the ground truth map
		if plot:
			plt.show()

	# Save the image
	if save_plot:
		plt.savefig(save_path + title + '_map.png', bbox_inches='tight')

	return fig_predMap, fig_GTs

def _paletteGen():
    """
	(Private method) Genereates a Python dictionary 'pallete' where each index corresponds to a label4Class color.
	- 0 = Black
	- 1 = Green
	- 2 = Red
	- 3 = Blue
	- 4 = Cyan
	- 5 = Magenta
	- 6 = White

	Outputs
    ----------
	- 'pallete': Python dictionary with RGB colors por each label4Class.
	"""
    palette = {0: (0, 0, 0)}

    palette[0] = np.asarray(np.array([0,0,0])*255,dtype='uint8')
    palette[1] = np.asarray(np.array([0,1,0])*255,dtype='uint8')
    palette[2] = np.asarray(np.array([1,0,0])*255,dtype='uint8')
    palette[3] = np.asarray(np.array([0,0,1])*255,dtype='uint8')
    palette[4] = np.asarray(np.array([0,1,1])*255,dtype='uint8')
    #palette[5] = np.asarray(np.array([.49,0,1])*255,dtype='uint8')
    palette[5] = np.asarray(np.array([1,0,1])*255,dtype='uint8')
    palette[6] = np.asarray(np.array([1,1,1])*255,dtype='uint8')

    return palette

def _convert2color(gt_raw, palette=_paletteGen()):
    """
	(Private method) Convert the Ground truth map with label4Classes to a color map.

	Inputs
    ----------
	- 'gt_raw':		Numpy array. Raw ground truth map with label4Classes.
	- 'pallete': 	Python dictionary with RGB colors for each label4Class.

	Outputs
    ----------
	- 'gt_color':	Numpy array with same shape as 'gt_raw' with colors for every label4Class.
	"""
	
    # Create empty array to create an RGB imagen with MxMx3 dimensions
    gt_color = np.zeros((gt_raw.shape[0], gt_raw.shape[1], 3), dtype=np.uint8)

	# Get the key and value from the dictionary to iterate (the label4Class and its color)
    for label4Class, color in palette.items():
        # get mask of vals that gt == #item in palette
        m = (gt_raw == label4Class)
        # set color val in 3 components
        gt_color[m] = color

    return gt_color

#*
#*#### END DEFINED METHODS #####
#*##############################