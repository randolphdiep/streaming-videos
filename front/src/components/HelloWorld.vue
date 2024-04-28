<template>
  <div>
    <video ref="videoPlayer" controls autoplay></video>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'HelloWorld',
  setup() {
    const videoPlayer = ref(null);

    const streamVideo = async () => {
      const fileId = '20240414124036'; // Replace with your file ID
      try {
        const response = await axios.get(`http://localhost:8000/stream-video/${fileId}`, { responseType: 'blob' });
        const videoBlob = new Blob([response.data], { type: 'video/mp4' });
        const videoUrl = URL.createObjectURL(videoBlob);
        videoPlayer.value.src = videoUrl;
      } catch (error) {
        console.error('Error streaming video:', error);
      }
    };

    onMounted(streamVideo);

    return { videoPlayer };
  }
});
</script>