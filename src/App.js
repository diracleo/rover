import React, {useEffect, useRef, useState} from 'react';
import logo from './logo.svg';
import './App.css';
import nipplejs from 'nipplejs';

function App() {
  const maxForce = 2.5;
  const maxInput = 255;
  const left = useRef(null);
  const right = useRef(null);
  let leftData = 0;
  let rightData = 0;
  let leftForce = 0;
  let rightForce = 0;
  let leftDir = 1;
  let rightDir = 1;
  let prevLeftData = null;
  let prevRightData = null;
  let commandTimer = null;
  
  function convertToInput(value, dir) {
    value = Math.round(value / maxForce * maxInput);
    if (value > maxInput) {
	  value = maxInput;
	}
	value *= dir;
	return value;
  }
  
  useEffect(() => {
    const optionsLeft = {
      zone: left.current,
      lockY: true,
      shape: "square",
    };
    const managerLeft = nipplejs.create(optionsLeft);
    const optionsRight = {
      zone: right.current,
      lockY: true,
      shape: "square",
    };
    const managerRight = nipplejs.create(optionsRight);
    
    managerLeft.on('start end', (evt, data) => {
      leftData = 0;
    }).on('move', (evt, data) => {
	  leftData = convertToInput(data.force, leftDir);
    }).on('dir:up', (evt, data) => {
      leftDir = 1;
    }).on('dir:down', (evt, data) => {
      leftDir = -1;
    });
    
    managerRight.on('start end', (evt, data) => {
      rightData = 0;
    }).on('move', (evt, data) => {
      rightData = convertToInput(data.force, rightDir);
    }).on('dir:up', (evt, data) => {
      rightDir = 1;
    }).on('dir:down', (evt, data) => {
      rightDir = -1;
    });
    
    commandTimer = setInterval(() => {
      if (leftData !== prevLeftData || rightData !== prevRightData) {
        let q = '';
		q += 'left='+leftData;
		q += '&right='+rightData;
        fetch('command/?'+q)
        .then(response => response.json())
        .then((data) => {
          prevLeftData = parseInt(data.left);
          prevRightData = parseInt(data.right);
        });
      }
    }, 200);
    
  }, []);
  return (
    <div className="App">
      <div id="left" ref={left}></div>
      <div id="right" ref={right}></div>
    </div>
  );
}

export default App;
