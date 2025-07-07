const API = "https://YOUR‑BACKEND‑HOSTNAME/lc";   // update once you deploy

function byId(id){ return document.getElementById(id); }

byId("frm").addEventListener("submit", async ev=>{
  ev.preventDefault();
  const ra = byId("ra").value, dec = byId("dec").value;
  const radius = byId("radius").value || "1.0";
  byId("msg").textContent = "⏳ querying…";
  byId("plot").innerHTML = "";

  try {
    const url = `${API}?ra=${ra}&dec=${dec}&radius=${radius}`;
    const resp = await fetch(url);
    if(!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();   // {MJD:[], psfFlux:[], psfFluxErr:[], filter:[], flag:[]}

    // group by filter for colouring
    const byBand = {};
    data.filter.forEach((b, i)=>{
      if(!byBand[b]) byBand[b] = {x:[], y:[], error_y:{type:"data", array:[], visible:true}, name:b};
      byBand[b].x.push(data.MJD[i]);
      byBand[b].y.push(data.psfFlux[i]);
      byBand[b].error_y.array.push(data.psfFluxErr[i]);
    });

    Plotly.newPlot("plot", Object.values(byBand),
      {xaxis:{title:"MJD"}, yaxis:{title:"psfFlux"}, title:`Light‑curve (${ra}, ${dec})`});

    byId("msg").textContent = `✅ ${data.MJD.length} points`;
  } catch(e){
    byId("msg").textContent = "❌ " + e.message.slice(0,400);
  }
});
