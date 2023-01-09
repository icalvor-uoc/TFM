console.log('Mounting Vue app on #app')

async function postRequest(path, args) {
    var sent_gr = JSON.stringify(args)
    const response = await fetch(window.location + path, {
		  method: 'post',
		  headers: {
		     'Content-Type' : 'application/json',
			 'X-Requested-With': 'XMLHttpRequest'
		  },
		  body: sent_gr
		})
    return await response.json()
}

async function getRequest(path, args) {
	
	var prefix = 'https://raw.githubusercontent.com/icalvor-uoc/TFM/main'
	
	var url = new URL(prefix + path)
	// url.search = new URLSearchParams(args).toString()
			
	const response = await fetch(url, {
		  method: 'get',
		  headers: {
		     'Content-Type' : 'application/json',
			 'X-Requested-With': 'XMLHttpRequest'
		  },
	})

	return await response.json()
}

var vueApp = new Vue({
  delimiters: ['{^vue^', '^vue^}'],
  el: '#app',
  async created(){
      await this.getGraph()
      await this.getGraphRefinement()
  },
  
  data: {
        active_panel: 1,
        active_extraction: 0,

        selected_graph: 1,

	    grefinement_list: [
		{name: 'Import',
		value: 2}
	    ],
	  	selected_grefinement: {
			name: 'Import',
			value: 2
	    },

        extraction_list: [

		],
	    selected_extraction: {

	    },

        extraction_prefix: '',
        extraction_number: 1,
        extraction_page: '',

        graph_refinement : {statements : []},
        new_grefinement: '',
	  
        fetch_list: [
        ],
        selected_fetch: {	
	      },
	  
	    fetch_refinement: {},
	    new_frefinement: '',

	    frefinement_list: [
	    ],
	    selected_frefinement: {},

	    nerd_list: [
	  
	    ],
	    selected_nerd: {},

	    nerd_refinement: {},
        new_nrefinement: '',

        nrefinement_list: [

		],

        selected_nrefinement: {

        },
	  
        triplegen_list: [
        
        ],
        
        selected_triplegen: {},

	    triplegen_refinement: {},
        new_tgrefinement: '',

        tgrefinement_list: [
        ],
        selected_tgrefinement: {},

        tripleval_list: [
        ],
	    selected_tripleval: {},

        tripleval_refinement: [
	    ],
        new_terefinement: '',

        terefinement_list: [
        ],
        selected_terefinement: {},
    },

  methods: {
	async switchQuality(index, q) {
		this.tripleval_refinement.units[index].quality = q
	},
	async switchCertainty(index, c) {
		this.tripleval_refinement.units[index].certainty = c
	},
	async switchPanel(i) {
		this.active_panel = i
		
    },
	async getGraphRefinement(){
		
		this.graph_refinement = {statements: []};
		await this.getExtraction()
		return;
		
        if (this.selected_grefinement.value == undefined) {
			r = {statements: []}
		} else {
		r = await getRequest('/read/grefinement', {selected_grefinement: this.selected_grefinement['value']})
        }


		this.graph_refinement = r
		
		await this.getExtraction()
	},
	async getGraph(){
		
		return;
		
		r = await getRequest('/filters/grefinement', {selected_graph: this.selected_graph})
        if (r['grefinement_list'].length > 0) {
            this.selected_grefinement = r.grefinement_list[0]
		} else {
            this.selected_grefinement = {}
		}
		this.grefinement_list = r.grefinement_list
		await this.getGraphRefinement()
	},
	async getExtraction(){
	    if (this.selected_grefinement.value == undefined) {
			r ={extraction_list:[]}
		} else {
	    this.active_extraction = 0
		r = await getRequest('/filters/extraction/'+2, {selected_grefinement: this.selected_grefinement['value']})
        }
		
		this.extraction_list = [
	      {
		    name: "None",
		    page: '',
		    value: 1
	      } 
		]
		this.extraction_list = this.extraction_list.concat(r)
		this.selected_extraction = this.extraction_list[0]
		await this.getPreFetch()
		

	},
	async getPreFetch(){
	    if (this.selected_extraction['name'] == 'None') {
			this.active_extraction = 0
			r ={fetch_list:[{}]}
		} else {
		this.active_extraction = 1
		r = await getRequest('/filters/fetch/'+this.selected_extraction['value'], {selected_extraction: this.selected_extraction['value']})
        }
		
		this.selected_fetch = r[0]
		this.fetch_list = r
		
		this.active_panel = 1
		
		await this.getFetch()
		
	},
	async getFetch(){
		if (this.selected_fetch == undefined || this.selected_fetch.value == undefined) {
			r ={frefinement_list:[{}]}
		} else {
		r = await getRequest('/filters/frefinement/'+this.selected_fetch['value'], {selected_fetch: this.selected_fetch['value']})
        }

		this.selected_frefinement = r[0]
		this.frefinement_list = r
		
		await this.getFRefinement()
		await this.getPreNerd()
		
	},
	async getNerd(){
		if (this.selected_nerd == undefined || this.selected_nerd.value == undefined) {
			r ={nrefinement_list:[{}]}
	    } else {
		r = await getRequest('/filters/nrefinement/'+this.selected_nerd['value'], {selected_nerd: this.selected_nerd['value']})
        }

		this.selected_nrefinement = r[0]
		this.nrefinement_list = r
		await this.getNRefinement()
		await this.getPreTriplegen()
		
	},
	async getTriplegen(){
        if (this.selected_triplegen == undefined || this.selected_triplegen.value == undefined) {
			r ={tgrefinement_list:[{}]}
		} else {
		r = await getRequest('/filters/tgrefinement/'+this.selected_triplegen['value'], {selected_triplegen: this.selected_triplegen['value']})
        }

		this.selected_tgrefinement = r[0]
		this.tgrefinement_list = r
		await this.getTGRefinement()
        await this.getPreTripleval()
		
	},
	async getTripleval(){
        if (this.selected_tripleval == undefined || this.selected_tripleval.value == undefined) {
		    r = {terefinement_list:[{}]}
		} else {
		r = await getRequest('/filters/terefinement/'+this.selected_tripleval['value'], {selected_tripleval: this.selected_tripleval['value']})
        }

		this.selected_terefinement = r[0]
		this.terefinement_list = r
		await this.getTERefinement()
	},
	async getPreNerd() {
        if (this.selected_frefinement.value == undefined) {
			r ={nerd_list:[{}]}
		} else {
		r = await getRequest('/filters/nerd/'+this.selected_frefinement['value'], {selected_frefinement: this.selected_frefinement['value']})
        }

		this.selected_nerd = r[0]
		this.nerd_list = r
		await this.getNerd()
    },
	async getPreTriplegen() {
        if (this.selected_nrefinement.value == undefined) {
			r ={triplegen_list:[{}]}
		} else {
		r = await getRequest('/filters/triplegen/'+this.selected_nrefinement['value'], {selected_nrefinement: this.selected_nrefinement['value']})
        }
		
		this.selected_triplegen = r[0]
		this.triplegen_list = r
		
		await this.getTriplegen()
    },
	async getPreTripleval() {
        if (this.selected_tgrefinement.value == undefined) {
			r ={tripleval_list:[{}]}
		} else {
		r = await getRequest('/filters/tripleval', {selected_tgrefinement: this.selected_tgrefinement['value']})
        }

		this.selected_tripleval = r[0]
		this.tripleval_list = r
		await this.getTripleval()
    },
	
	async getFRefinement(){
        if (this.selected_frefinement.value == undefined) {
			r ={}
		} else {
		r = await getRequest('/read/frefinement/'+this.selected_frefinement['value'], {selected_frefinement: this.selected_frefinement['value']})
		}
		
		this.fetch_refinement = r

	},
	async getNRefinement(){
        if (this.selected_nrefinement.value == undefined) {
			r = {}
		} else {
		r = await getRequest('/read/nrefinement/'+this.selected_nrefinement['value'], {selected_nrefinement: this.selected_nrefinement['value']})
        }
		this.nerd_refinement = r
	},
	async getTGRefinement(){
        if (this.selected_tgrefinement.value == undefined) {
			r = {}
		} else {
		r = await getRequest('/read/tgrefinement/'+this.selected_tgrefinement['value'], {selected_tgrefinement: this.selected_tgrefinement['value']})
        }
		
		this.triplegen_refinement = r

	},
	async getTERefinement(){
		
		return;
		
        if (this.selected_terefinement.value == undefined) {
			r = {}
		} else {
		r = await getRequest('/read/terefinement', {selected_terefinement: this.selected_terefinement['value']})
        }
		
		this.tripleval_refinement = r

	},
	async cu_graphrefinement() {
		
		return;
		
      if (this.new_grefinement != '') {
		r = await postRequest('/create/grefinement', {
			           graph_refinement: this.graph_refinement,
					   selected_graph: this.selected_graph,
					   name: this.new_grefinement
					   })
	  } else {
		  	    if (this.selected_grefinement.value == undefined) {
			return
		}
		r = await postRequest('/update/grefinement', {

			           graph_refinement: this.graph_refinement,
					   selected_grefinement: this.selected_grefinement['value']
					   })
	  }
		this.new_grefinement = ''
		await this.getGraph()
		await this.getGraphRefinement()
	},
	async new_extraction_url() {
		
		return;
		
		if (this.extraction_page == '') {
		  alert("Enter the URL of the wikipedia's page")
		  return
		}
		r = await postRequest('/create/extraction_url', {
			           extraction_page: this.extraction_page,
					   selected_grefinement: this.selected_grefinement['value']
					   })

		this.extraction_page = ''
		await this.getExtraction()
	},
	async new_extraction_prefix() {
		
		return;
		
		if (this.extraction_prefix == '') {
		  alert("Enter a prefix for the new graph refinement")
		  return
		}
		r = await postRequest('/create/extraction_prefix', {
			           extraction_number: this.extraction_number,
			           extraction_prefix: this.extraction_prefix,
					   selected_grefinement: this.selected_grefinement['value']
					   })

		this.extraction_prefix = ''
		await this.getExtraction()
	},
	async cuFRefinement() {
		
		return;
		
		if (this.selected_frefinement['is_none'] && this.new_frefinement == '') {
		  alert("Enter a name for the new fetch refinement")
		  return
		}
        if (this.new_frefinement != '') {
           if (this.selected_fetch.value == undefined) {
			  return
		   } else {
			r = await postRequest('/create/frefinement', {
			           fetch_refinement: this.fetch_refinement,
					   selected_fetch: this.selected_fetch['value'],
					   name: this.new_frefinement
					   })
		   }
		} else {
		  if (this.selected_frefinement.value == undefined) {
			return
		  } else {
			r = await postRequest('/update/frefinement', {
			           fetch_refinement: this.fetch_refinement,
					   selected_frefinement: this.selected_frefinement['value'],
					   })
	      }
		}

		this.new_frefinement = ''
		await this.getFetch()
	},
	async cuNRefinement() {
		
		return;
		
		if (this.selected_nrefinement['is_none'] && this.new_nrefinement == '') {
		  alert("Enter a name for the new entextr refinement")
		  return
		}

        if (this.new_nrefinement != '') {
		  if (this.selected_nerd.value == undefined) {
			return
		  } else {
			r = await postRequest('/create/nrefinement', {
			           nerd_refinement: this.nerd_refinement,
					   selected_nerd: this.selected_nerd['value'],
					   name: this.new_nrefinement
					   })
		  }
		} else {
		  if (this.selected_nrefinement.value == undefined) {
			return
		  } else {
			r = await postRequest('/update/nrefinement', {
			           nerd_refinement: this.nerd_refinement,
					   selected_nrefinement: this.selected_nrefinement['value'],
					   })
		  }
		}

		this.new_nrefinement = ''
		await this.getPreNerd()
	},
	async cuTGRefinement() {
		
		return;
		
		if (this.selected_tgrefinement['is_none'] && this.new_tgrefinement == '') {
		  alert("Enter a name for the new triplegen refinement")
		  return
		}

        if (this.new_tgrefinement != '') {
          if (this.selected_triplegen.value == undefined) {
			return
		  } else {
			r = await postRequest('/create/tgrefinement', {
			           triplegen_refinement: this.triplegen_refinement,
					   selected_triplegen: this.selected_triplegen['value'],
					   name: this.new_tgrefinement
					   })
		  }
		} else {
          if (this.selected_tgrefinement.value == undefined) {
			return
	  	} else {
			r = await postRequest('/update/tgrefinement', {
			           triplegen_refinement: this.triplegen_refinement,
					   selected_tgrefinement: this.selected_tgrefinement['value'],
					   })
		}
		}

		this.new_tgrefinement = ''
		await this.getPreTriplegen()
	},
	async cuTERefinement() {
		
		return;
		
		if (this.selected_terefinement['is_none'] && this.new_terefinement == '') {
		  alert("Enter a name for the new tripleval refinement")
		  return
		}

        if (this.new_terefinement != '') {
          if (this.selected_tripleval.value == undefined) {
			return
	      } else {
			r = await postRequest('/create/terefinement', {
			           tripleval_refinement: this.tripleval_refinement,
					   selected_tripleval: this.selected_tripleval['value'],
					   name: this.new_terefinement
					   })
		  }
		} else {
          if (this.selected_terefinement.value == undefined) {
			return
	  	} else {
			r = await postRequest('/update/terefinement', {
			           tripleval_refinement: this.tripleval_refinement,
					   selected_terefinement: this.selected_terefinement['value'],
					   })
		  }
		}

		this.new_terefinement = ''
		await this.getPreTripleval()
	},
	async d_graphrefinement()  {
		
		return;
		
		if (this.selected_grefinement.value == undefined) {
			return
		} else {
	  r = await postRequest('/remove/grefinement', {selected_grefinement: this.selected_grefinement['value']})
        }
		
		this.new_grefinement = ''
	  
		await this.getGraph()
		await this.getGraphRefinement()
    	
  },
	async delFRefinement()  {
		
		return;
		
	  if (this.selected_frefinement['is_none'] || this.selected_frefinement.value == undefined) {
			return
		} else {
	  r = await postRequest('/remove/frefinement', {selected_frefinement: this.selected_frefinement['value']})
		}
		this.new_frefinement = ''
	  
		await this.getFetch()
    },
    async delNRefinement() {
		
		return;
		
	  if (this.selected_nrefinement['is_none']) {
	    return
	  } else {
	  r = await postRequest('/remove/nrefinement', {selected_nrefinement: this.selected_nrefinement['value']})
	  }
		this.new_nrefinement = ''
	  
		await this.getPreNerd()
	},
    async delTGRefinement() {
		
		return;
		
	  if (this.selected_tgrefinement['is_none'] || this.selected_tgrefinement.value == undefined) {
			return
		} else {
	  r = await postRequest('/remove/tgrefinement', {selected_tgrefinement: this.selected_tgrefinement['value']})
		}
		this.new_tgrefinement = ''
	  
		await this.getPreTriplegen()
	},
    async delTERefinement() {
		
		return;
		
	  if (this.selected_terefinement['is_none'] || this.selected_terefinement.value == undefined) {
			return
		} else {
	  r = await postRequest('/remove/terefinement', {selected_terefinement: this.selected_terefinement['value']})
		}
		this.new_terefinement = ''
	  
		await this.getPreTripleval()
	},
	
	
	
	
	async listClicked(list) {
      console.log(list)
      for  (item of list) {
		 alert(item)
	  }
	},
	
	
  },
  
  components: {
	fetch_section: {
		template: '#fetch_section_component',
		name: 'fetch_section',
        delimiters: ['{^vue^', '^vue^}'],
		props: { section: Object },
		methods: {
			async placeholder() {
				alert(this.section.title)
			}
		}
		
	},
	
	nerd_section: {
		template: '#nerd_section_component',
		name: 'nerd_section',
        delimiters: ['{^vue^', '^vue^}'],
		props: { section: Object },
		methods: {
			async placeholder() {
				alert(this.section.title)
			}
		}
		
	}
	  
  }

	
  
})
