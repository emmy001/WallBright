import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getFirestore, collection, getDocs } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Firebase
    const firebaseConfig = {
      apiKey: "AIzaSyDdL99XWn7dE4eYCm8GMxYcxuaA3Jm4dUo",
      authDomain: "smartattendance-cb35b.firebaseapp.com",
      databaseURL: "https://smartattendance-cb35b-default-rtdb.firebaseio.com",
      projectId: "smartattendance-cb35b",
      storageBucket: "smartattendance-cb35b.appspot.com",
      messagingSenderId: "203482295003",
      appId: "1:203482295003:web:bea6ad1b84a52645467afe",
      measurementId: "G-4JH9DDMNSF"
    };

    // Function to fetch data from Firestore
    const app = initializeApp(firebaseConfig); // Initialize Firebase app
    const firestore = getFirestore(app); // Get Firestore instance from Firebase app

    // Function to fetch data from Firestore
    async function fetchDataFromFirestore() {
        const querySnapshot = await getDocs(collection(firestore, 'Students'));
        const data = {};
        querySnapshot.forEach((doc) => {
            const docData = doc.data();
            // Extract only the desired fields from the document data
            const selectedData = {
                classes: docData.classes,
                name: docData.name,
                email: docData.email,
                usertype:docData.usertype
            };
            data[doc.id] = selectedData; // Add each document with selected fields to the data object
        });
        return data;
    }

    // Function to display chart with fetched data
    function displayChartWithData(data) {
        // Process the fetched data and create datasets for the chart
        const labels = Object.keys(data);
        const datasets = [{
            label: 'Students by Class',
            data: Object.values(data),
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }];

        // Configure the chart
        const ctx = document.getElementById('attendance-chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'bar',
            data: { labels, datasets },
            options: {
                // Add any additional options for the chart
            }
        });
    }

    // Fetch data from Firestore and display chart
    fetchDataFromFirestore()
        .then((data) => {
            if (data) {
                // Once data is fetched, display chart
                displayChartWithData(data);
            }
        });
});