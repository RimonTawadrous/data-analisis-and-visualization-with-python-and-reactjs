import React from 'react'
import {Bar} from "react-chartjs-2"
import "./BarChart.css"

const BarChart = ({labels,data,inputLabel,colorsList}) => {
    return (
        <div>
           <Bar data={{labels:labels,
                  datasets:[
                    {
                    label: inputLabel,
                    data: data,
                    backgroundColor: colorsList
                    }
                    ]}} height={400} width={100} options={{maintainAspectRatio:false}}/> 
        </div>
    )
}

export default BarChart
