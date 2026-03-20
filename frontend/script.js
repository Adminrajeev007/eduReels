// ============================================================================
// EducationalReels Frontend - JavaScript
// ============================================================================

// Configuration
const API_BASE_URL = "/api"; // This will be configured during deployment
const LOCALHOST_URL = "http://localhost:8000";

// DOM Elements
const degreeSelect = document.getElementById("degree-select");
const generateBtn = document.getElementById("generate-btn");
const loadingMessage = document.getElementById("loading-message");
const errorMessage = document.getElementById("error-message");
const resultsSection = document.getElementById("results-section");

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener("DOMContentLoaded", function () {
	console.log("EducationalReels Frontend Loaded");

	// Enable/disable generate button based on selection
	degreeSelect.addEventListener("change", function () {
		generateBtn.disabled = !this.value;
	});

	// Generate button click handler
	generateBtn.addEventListener("click", handleGenerate);

	// Check API connectivity
	checkAPIHealth();
});

// ============================================================================
// API Functions
// ============================================================================

async function getAPIUrl() {
	/**
	 * Determine the correct API URL
	 * In production: Use relative path /api
	 * In development: Use localhost:8000
	 */
	try {
		// Try production URL first
		const response = await fetch("/api/health", { method: "HEAD" });
		if (response.ok) return "/api";
	} catch (e) {
		// Fall back to localhost
	}

	try {
		const response = await fetch(`${LOCALHOST_URL}/health`, { method: "HEAD" });
		if (response.ok) return LOCALHOST_URL;
	} catch (e) {
		// Neither works
	}

	return LOCALHOST_URL; // Default fallback
}

async function checkAPIHealth() {
	try {
		const apiUrl = await getAPIUrl();
		const response = await fetch(`${apiUrl}/health`);
		if (!response.ok) {
			console.warn("API health check failed");
		}
	} catch (e) {
		console.warn("Could not connect to API:", e.message);
	}
}

async function generateContent() {
	const degree = degreeSelect.value;

	if (!degree) {
		showError("Please select a subject");
		return null;
	}

	try {
		const apiUrl = await getAPIUrl();
		const response = await fetch(`${apiUrl}/generate`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ degree }),
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.detail || "Failed to generate content");
		}

		return await response.json();
	} catch (error) {
		showError(`Error: ${error.message}`);
		console.error("Generation error:", error);
		return null;
	}
}

// ============================================================================
// Event Handlers
// ============================================================================

async function handleGenerate() {
	hideError();
	hideResults();
	showLoading();
	generateBtn.disabled = true;

	const result = await generateContent();

	hideLoading();
	generateBtn.disabled = false;

	if (result) {
		displayResults(result);
	}
}

function generateNew() {
	degreeSelect.value = "";
	generateBtn.disabled = true;
	hideResults();
	hideError();
}

// ============================================================================
// Display Functions
// ============================================================================

function displayResults(data) {
	try {
		// Basic Information
		document.getElementById("question-text").textContent = data.reel_question || "N/A";
		document.getElementById("topic-text").textContent = data.topic || "N/A";
		document.getElementById("answer-text").textContent = data.reel_answer || "N/A";

		// Enhanced Content (Week 3)
		const simplifiedText = document.getElementById("simplified-text");
		const analogyText = document.getElementById("analogy-text");
		const primaryExampleText = document.getElementById("primary-example-text");
		const secondaryExamplesList = document.getElementById("secondary-examples-list");
		const hookText = document.getElementById("hook-text");
		const tipsList = document.getElementById("tips-list");

		if (data.simplified_answer) {
			simplifiedText.textContent = data.simplified_answer;
		} else {
			simplifiedText.parentElement.classList.add("hidden");
		}

		if (data.analogy) {
			analogyText.textContent = data.analogy;
		} else {
			analogyText.parentElement.classList.add("hidden");
		}

		if (data.primary_example) {
			primaryExampleText.textContent = data.primary_example;
		} else {
			primaryExampleText.parentElement.classList.add("hidden");
		}

		if (data.secondary_examples && data.secondary_examples.length > 0) {
			secondaryExamplesList.innerHTML = "";
			data.secondary_examples.forEach((example) => {
				const li = document.createElement("li");
				li.textContent = example;
				secondaryExamplesList.appendChild(li);
			});
		} else {
			secondaryExamplesList.parentElement.classList.add("hidden");
		}

		if (data.hook) {
			hookText.textContent = data.hook;
		} else {
			hookText.parentElement.classList.add("hidden");
		}

		if (data.engagement_tips && data.engagement_tips.length > 0) {
			tipsList.innerHTML = "";
			data.engagement_tips.forEach((tip) => {
				const li = document.createElement("li");
				li.textContent = tip;
				tipsList.appendChild(li);
			});
		} else {
			tipsList.parentElement.classList.add("hidden");
		}

		// Metrics
		const durationText = document.getElementById("duration-text");
		const engagementScoreText = document.getElementById("engagement-score-text");
		const platformsText = document.getElementById("platforms-text");

		if (data.video_duration_seconds) {
			durationText.textContent = `${data.video_duration_seconds} seconds`;
		} else {
			durationText.textContent = "N/A";
		}

		if (data.engagement_score !== undefined && data.engagement_score !== null) {
			engagementScoreText.textContent = `${data.engagement_score.toFixed(1)}/10`;
		} else {
			engagementScoreText.textContent = "N/A";
		}

		if (data.platform_recommendations && data.platform_recommendations.length > 0) {
			platformsText.textContent = data.platform_recommendations.join(", ");
		} else {
			platformsText.textContent = "N/A";
		}

		// Metadata
		document.getElementById("metadata-degree").textContent = data.degree || "N/A";
		document.getElementById("metadata-time").textContent = `${(data.generation_time || 0).toFixed(2)}s`;
		document.getElementById("metadata-cached").textContent = data.cached ? "Yes (Cached)" : "No (Fresh)";
		document.getElementById("metadata-status").textContent = data.status ? data.status.toUpperCase() : "UNKNOWN";

		// Quality Badge
		const qualityBadge = document.getElementById("quality-badge");
		const qualityScore = data.quality_score || 0;
		qualityBadge.textContent = `Quality: ${qualityScore}/10`;

		if (qualityScore >= 8) {
			qualityBadge.style.background = "var(--success-color)";
		} else if (qualityScore >= 7) {
			qualityBadge.style.background = "var(--warning-color)";
		} else {
			qualityBadge.style.background = "var(--error-color)";
		}

		// Show results
		showResults();

		// Store current result for download
		window.lastResult = data;
	} catch (error) {
		showError("Error displaying results: " + error.message);
		console.error("Display error:", error);
	}
}

function showResults() {
	resultsSection.classList.remove("hidden");
	resultsSection.scrollIntoView({ behavior: "smooth" });
}

function hideResults() {
	resultsSection.classList.add("hidden");
}

function showLoading() {
	loadingMessage.classList.remove("hidden");
}

function hideLoading() {
	loadingMessage.classList.add("hidden");
}

function showError(message) {
	errorMessage.textContent = "❌ " + message;
	errorMessage.classList.remove("hidden");
}

function hideError() {
	errorMessage.classList.add("hidden");
}

// ============================================================================
// Utility Functions
// ============================================================================

function copyText(elementId) {
	const element = document.getElementById(elementId);
	const text = element.textContent;

	navigator.clipboard
		.writeText(text)
		.then(() => {
			// Show feedback
			const btn = event.target;
			const originalText = btn.textContent;
			btn.textContent = "✅ Copied!";

			setTimeout(() => {
				btn.textContent = originalText;
			}, 2000);
		})
		.catch((err) => {
			showError("Failed to copy text");
			console.error("Copy error:", err);
		});
}

function downloadJSON() {
	if (!window.lastResult) {
		showError("No content to download");
		return;
	}

	const dataStr = JSON.stringify(window.lastResult, null, 2);
	const dataBlob = new Blob([dataStr], { type: "application/json" });
	const url = URL.createObjectURL(dataBlob);

	const link = document.createElement("a");
	link.href = url;
	link.download = `educational-reel-${window.lastResult.topic.replace(/\s+/g, "-")}.json`;
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
	URL.revokeObjectURL(url);
}

function shareContent() {
	if (!window.lastResult) {
		showError("No content to share");
		return;
	}

	const text = `📚 EducationalReels\n\nSubject: ${window.lastResult.degree}\nTopic: ${window.lastResult.topic}\n\nQuestion: ${window.lastResult.reel_question.substring(0, 100)}...`;

	if (navigator.share) {
		navigator
			.share({
				title: "EducationalReels",
				text: text,
				url: window.location.href,
			})
			.catch((err) => {
				if (err.name !== "AbortError") {
					console.error("Share error:", err);
				}
			});
	} else {
		// Fallback: Copy to clipboard
		navigator.clipboard.writeText(`${text}\n\nGenerated by EducationalReels`).then(() => {
			showError("Content copied to clipboard (Web Share not available)");
		});
	}
}

// ============================================================================
// Keyboard Shortcuts
// ============================================================================

document.addEventListener("keydown", function (event) {
	// Ctrl/Cmd + Enter to generate
	if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
		if (!generateBtn.disabled) {
			handleGenerate();
		}
	}

	// Escape to hide error
	if (event.key === "Escape") {
		hideError();
	}
});

// ============================================================================
// Logging
// ============================================================================

console.log("EducationalReels Frontend v1.0.0");
console.log("API Base URL:", LOCALHOST_URL);
