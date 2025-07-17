const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const os = require('os');
const fs = require('fs');

/**
 * Extracts a specified number of random frames from a video file.
 *
 * @param {string} videoPath - The path to the input video file.
 * @param {number} frameCount - The number of random frames to extract.
 * @returns {Promise<string>} A promise that resolves with the path to the directory
 * containing the extracted frames.
 */
function extractRandomFrames(videoPath, frameCount = 10) {
    return new Promise((resolve, reject) => {
        // 1. Get video metadata to determine its duration
        ffmpeg.ffprobe(videoPath, (err, metadata) => {
            if (err) {
                console.error('Error reading video metadata:', err.message);
                return reject(err);
            }

            const duration = metadata.format.duration;
            if (!duration) {
                return reject(new Error('Could not determine video duration.'));
            }

            // 2. Generate an array of random, unique timestamps within the video's duration
            const timestamps = [];
            for (let i = 0; i < frameCount; i++) {
                timestamps.push(Math.random() * duration);
            }
            // Sorting is not required but can be good practice
            timestamps.sort((a, b) => a - b);

            // 3. Create a unique temporary directory for the output frames
            const outputDir = path.join(os.tmpdir(), `video-frames-${Date.now()}`);
            fs.mkdirSync(outputDir, { recursive: true });

            // 4. Use ffmpeg to extract frames at the generated timestamps
            ffmpeg(videoPath)
                .on('end', () => {
                    console.log(`Successfully extracted ${frameCount} frames to ${outputDir}`);
                    resolve(outputDir); // Resolve with the output directory path
                })
                .on('error', (error) => {
                    console.error('Error during frame extraction:', error.message);
                    reject(error);
                })
                .screenshots({
                    timemarks: timestamps, // An array of timestamps in seconds
                    folder: outputDir,
                    filename: 'frame-%i.png' // %i is the frame index
                });
        });
    });
}

// --- Example Usage ---
async function processVideo() {
    try {
        const videoFile = 'C:/Users/sanke/OneDrive/Desktop/Cabswale/videoVerification/intro.mp4';
        const framesDirectory = await extractRandomFrames(videoFile, 10);
        console.log('Frames are saved in:', framesDirectory);
        // You can now process the files in that directory
    } catch (error) {
        console.error('Failed to process video:', error);
    }
}

processVideo();