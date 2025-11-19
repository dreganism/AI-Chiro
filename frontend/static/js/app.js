fetch('/').then(r=>r.json()).then(d=>document.getElementById('status').innerText = d.message).catch(()=>document.getElementById('status').innerText = 'offline');
