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

    const app = initializeApp(firebaseConfig);
    const firestore = getFirestore(app);

    async function fetchDataForBar(collectionName, fields) {
        let collectionRef = collection(firestore, collectionName);
        const querySnapshot = await getDocs(collectionRef);
        const data = {};
        querySnapshot.forEach((doc) => {
            const docData = {};
            fields.forEach(field => {
                docData[field] = doc.data()[field];
            });
            data[doc.id] = docData;
        });
        return data;
        console.log("Data found forBar:", data);
    }
    async function fetchDataForPie(collectionName, fields) {
        let collectionRef = collection(firestore, collectionName);
        const querySnapshot = await getDocs(collectionRef);
        const data = {};
        querySnapshot.forEach((doc) => {
            const docData = {};
            fields.forEach(field => {
                docData[field] = doc.data()[field];
            });
            data[doc.id] = docData;
        });
        return data;
        console.log("Data found forpie:", data);
    }

    async function fetchDataForRadar(collectionName, fields) {
        let collectionRef = collection(firestore, collectionName);
        const querySnapshot = await getDocs(collectionRef);
        const data = {};
        querySnapshot.forEach((doc) => {
            const docData = {};
            fields.forEach(field => {
                docData[field] = doc.data()[field];
            });
            data[doc.id] = docData;
        });
        return data;
    }

    function processDataForBarGraph(data) {
        const BarGraphLabels = [];
        const BarGraphData = [];

        // Iterate over the data object
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                const item = data[key];
                // Push the name as label
                BarGraphLabels.push(item.name);
                // Calculate total classes for the student
                const totalClasses = Object.values(item.classes).reduce((acc, cur) => acc + cur, 0);
                // Push the total classes as data
                BarGraphData.push(totalClasses);
            }
        }

        return {
            labels: BarGraphLabels,
            datasets: [{
                label: 'Bar Graph Label',
                data: BarGraphData,
                backgroundColor: 'rgba(75, 175, 111, 0.6)',
                borderColor: 'rgba(82, 189, 125, 1)',
                borderWidth: 1
            }]
        };
    }

    // Function to process data for the pie chart
    function processDataForPieChart(data) {
        const pieChartLabels = [];
        const pieChartData = [];

        // Iterate over the data object
        for (const key in data) {
            if (data.hasOwnProperty(key)) {
                const item = data[key];
                // Push the name as label
                pieChartLabels.push(item.name);
                // Calculate total classes for the student
                const totalClasses = Object.values(item.classes).reduce((acc, cur) => acc + cur, 0);
                // Push the total classes as data
                pieChartData.push(totalClasses);
            }
        }

        return {
            labels: pieChartLabels,
            datasets: [{
                data: pieChartData,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                    // Add more colors as needed
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                    // Add more colors as needed
                ],
                borderWidth: 1
            }]
        };
    }


    function processDataForRadarChart(data) {
    const radarChartLabels = [];
    const radarChartData = [];

    // Iterate over the data object
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            const item = data[key];
            // Calculate total classes for the student
            const totalClasses = Object.values(item.classes).reduce((acc, cur) => acc + cur, 0);
            // Check if total classes (attendance) is zero
            if (totalClasses === 0) {
                // Push the name as label
                radarChartLabels.push(item.daysOfWeek);
                // Push the total classes as data
                radarChartData.push(totalClasses);
            } else {
                // If student has attended classes, push their name and total classes attended
                radarChartLabels.push(item.daysOfWeek);
                radarChartData.push(totalClasses);
            }
        }
    }

    return {
        labels: radarChartLabels,
        datasets: [{
            label: 'Radar Chart Label',
            data: radarChartData,
            backgroundColor: ['rgba(255, 99, 132, 0.2)',
                              'rgba(54, 162, 235, 0.2)',
                              'rgba(255, 206, 86, 0.2)',
                              'rgba(75, 192, 192, 0.2)',
                              'rgba(153, 102, 255, 0.2)',
                              'rgba(255, 159, 64, 0.2)' ],
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
    };
}



    console.log("Fetching data for bar:");
    const barGraphData = await fetchDataForBar('Students', ['name', 'classes']);
    console.log("Bar chart data:", barGraphData);
    const pieChartData = await fetchDataForPie('Students', ['name', 'classes']);
    console.log("Pie chart data:", pieChartData);
    const radarChartData = await fetchDataForRadar('Students', ['dayOfWeek', 'classes']);
    console.log("Radar chart data:", radarChartData);

    const processedBarGraphData = processDataForBarGraph(barGraphData);
    console.log("processed data for bar:", processedBarGraphData);
    const processedPieChartData = processDataForPieChart(pieChartData);
    console.log("processed data for pie:", processedPieChartData);
    const processedRadarChartData = processDataForRadarChart(radarChartData);
    console.log("processes data for:", processedRadarChartData);

    console.log("Initializing bar chart");
    new Chart(document.getElementById('attendance-chart').getContext('2d'), {
        type: 'bar',
        data: processedBarGraphData,
        options: {}
    });
    console.log("Chart Initialization Complete");

    console.log("Initializing pie chart");
    new Chart(document.getElementById('pie').getContext('2d'), {
        type: 'pie',
        data: processedPieChartData,
        options: {}
    });
    console.log("Chart Initialization Complete");

    // Set the width and height of the 'pie' element
    //document.getElementById('pie').style.width = '400px'; // Set width to 300 pixels
    document.getElementById('pie').style.height = '390px'; // Set height to 300 pixels

    console.log("Initializing radar chart");
    new Chart(document.getElementById('radarChart').getContext('2d'), {
        type: 'radar',
        data: processedRadarChartData,
        options: {}
    });
    console.log("Chart Initialization Complete");
});
