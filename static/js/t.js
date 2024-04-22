import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getFirestore, collection, getDocs } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";


document.addEventListener('DOMContentLoaded', async function() {
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

    // Fetch data from Firestore
    const app = initializeApp(firebaseConfig);
    const firestore = getFirestore(app);

    const fetchedData = await fetchDataFromFirestore();


    // Process data for different charts
    const barChartData = processBarChartData(fetchedData);
    const pieChartData = processPieChartData(fetchedData);
    const radarChartData = processRadarChartData(fetchedData);

    // Display charts
    displayBarChart(barChartData);
    displayPieChart(pieChartData);
    displayRadarChart(radarChartData);
});

// Function to fetch data from Firestore
async function fetchDataFromFirestore() {
    const querySnapshot = await getDocs(collection(firestore, 'Students'));
    const data = {};
    querySnapshot.forEach((doc) => {
        const docData = doc.data();
        const selectedData = {
            classes: docData.classes,
            name: docData.name,
            email: docData.email,
            usertype: docData.usertype
        };
        data[doc.id] = selectedData;
    });
    return data;
}

// Function to process data for the bar chart
function processBarChartData(data) {
    const barChartData = {
        labels: [],
        values: []
    };
    for (const id in data) {
        const student = data[id];
        barChartData.labels.push(student.name);
        barChartData.values.push(student.classes);
    }
    return barChartData;
}

// Function to process data for the pie chart
function processPieChartData(data) {
    const pieChartData = {};
    for (const id in data) {
        const student = data[id];
        pieChartData[student.name] = student.classes;
    }
    return pieChartData;
}

// Function to process data for the radar chart
function processRadarChartData(data) {
    const radarChartData = {
        labels: [],
        values: []
    };
    for (const id in data) {
        const student = data[id];
        radarChartData.labels.push(student.name);
        radarChartData.values.push(student.classes);
    }
    return radarChartData;
}

// Function to display the bar chart
function displayBarChart(data) {
    // Use Chart.js or any other library to create and display the bar chart
}

// Function to display the pie chart
function displayPieChart(data) {
    // Use Chart.js or any other library to create and display the pie chart
}

// Function to display the radar chart
function displayRadarChart(data) {
    // Use Chart.js or any other library to create and display the radar chart
}
