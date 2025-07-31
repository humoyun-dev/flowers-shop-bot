"use client";

import { useEffect, useState } from "react";
import { Minus, Plus, Trash2, ShoppingCart, Phone } from "lucide-react";

const tg = window.Telegram?.WebApp;
const url = "https://9c12531e16df.ngrok-free.app/";

export default function FlowerShop() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [phone, setPhone] = useState("");
  const [imageUrls, setImageUrls] = useState({});

  console.log(`${url}products`);

  useEffect(() => {
    if (tg?.ready) tg.ready();
    const fetchProducts = async () => {
      try {
        const res = await fetch(`${url}products`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
          },
        });
        const data = await res.json();
        const urls = {};
        await Promise.all(
          data.map(async (product) => {
            if (product.image && product.image.startsWith("AgACAg")) {
              const res = await fetch(`${url}file/${product.image}`, {
                method: "GET",
                headers: {
                  "Content-Type": "application/json",
                  "ngrok-skip-browser-warning": "true",
                },
              });
              const file = await res.json();
              urls[product.image] = file.url;
            }
          }),
        );
        setImageUrls(urls);
        setProducts(data);
      } catch (err) {
        console.log(err);
        console.error("Mahsulotlarni olishda xatolik:", err);
      }
    };
    fetchProducts();
  }, []);

  const updateCart = (product, delta) => {
    setCart((prev) => {
      const item = prev.find((i) => i.id === product.id);

      if (item) {
        const newQuantity = item.quantity + delta;
        if (newQuantity > product.count) {
          alert(
            `Mavjud miqdordan oshib ketdingiz! Mahsulot ID ${product.id} uchun ${product.count} ta mavjud.`,
          );
          return prev;
        }
        if (newQuantity <= 0) {
          return prev.filter((i) => i.id !== product.id);
        }
        return prev.map((i) =>
          i.id === product.id ? { ...i, quantity: newQuantity } : i,
        );
      } else if (delta > 0) {
        if (product.count > 0) {
          return [...prev, { ...product, quantity: 1 }];
        } else {
          alert(`Mahsulot ID ${product.id} hozirda mavjud emas.`);
          return prev;
        }
      }
      return prev;
    });
  };

  const calculateTotal = () =>
    cart.reduce((sum, i) => sum + i.price * i.quantity, 0);

  const sendOrder = () => {
    if (!phone || cart.length === 0) return;

    const order = {
      items: cart.map(({ id, quantity, price }) => ({
        product_id: id,
        amount: quantity,
        price,
      })),
      total_price: calculateTotal(),
    };

    tg?.sendData
      ? tg.sendData(JSON.stringify(order))
      : alert("Buyurtma yuborildi (test)");
    setCart([]);
    setPhone("");
  };

  const resolveImage = (image) => {
    return image && image.startsWith("AgACAg")
      ? imageUrls[image] || "/placeholder.svg"
      : image || "/placeholder.svg";
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans antialiased p-4 sm:p-8 lg:p-12">
      <header className="text-center mb-16">
        <h1 className="text-5xl sm:text-6xl font-extrabold text-gray-800 tracking-tight leading-tight">
          🌸 Gullar do‘koni
        </h1>
        <p className="text-xl text-gray-600 mt-4">
          Go‘zallikni yetkazib beramiz
        </p>
      </header>

      <main className="max-w-7xl mx-auto">
        <section className="mb-20">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-800 mb-10">
            Mahsulotlar
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {products.map((product) => {
              const item = cart.find((c) => c.id === product.id);
              const imageUrl = resolveImage(product.image);
              const currentQuantity = item ? item.quantity : 0;

              return (
                <div
                  key={product.id}
                  className="bg-white rounded-2xl shadow-xl overflow-hidden transform transition-all duration-300 hover:scale-[1.01] hover:shadow-2xl flex flex-col"
                >
                  <div className="relative w-full h-64 bg-gray-100 flex items-center justify-center">
                    <img
                      src={imageUrl || "/placeholder.svg"}
                      alt={`Mahsulot ID: ${product.id}`}
                      className="object-cover w-full h-full"
                      loading="lazy" // Optimize image loading
                    />
                  </div>
                  <div className="p-6 flex-grow flex flex-col justify-between">
                    <div>
                      <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                        Mahsulot ID: {product.id}
                      </h3>
                      <p className="text-xl font-bold text-pink-600 mb-3">
                        {product.price.toLocaleString()} so&apos;m
                      </p>
                      <p className="text-sm text-gray-500">
                        Mavjud: {product.count} ta
                      </p>
                    </div>
                    <div className="mt-6">
                      <div className="flex items-center justify-center gap-4 mb-6">
                        <button
                          onClick={() => updateCart(product, -1)}
                          className="p-3 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                          aria-label={`Decrease quantity of product ID ${product.id}`}
                          disabled={currentQuantity === 0}
                        >
                          <Minus className="h-6 w-6" />
                        </button>
                        <span className="font-bold text-2xl text-gray-900">
                          {currentQuantity}
                        </span>
                        <button
                          onClick={() => updateCart(product, 1)}
                          className="p-3 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                          aria-label={`Increase quantity of product ID ${product.id}`}
                          disabled={currentQuantity >= product.count}
                        >
                          <Plus className="h-6 w-6" />
                        </button>
                      </div>
                      {currentQuantity === 0 ? (
                        <button
                          onClick={() => updateCart(product, 1)}
                          className="w-full bg-pink-500 hover:bg-pink-600 text-white py-4 rounded-xl font-semibold text-xl transition-colors disabled:bg-pink-300 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                          disabled={product.count === 0}
                        >
                          ➕ Savatga qo&apos;shish
                        </button>
                      ) : (
                        <button
                          onClick={() => updateCart(product, -currentQuantity)}
                          className="w-full bg-red-500 hover:bg-red-600 text-white py-4 rounded-xl font-semibold text-xl transition-colors shadow-lg hover:shadow-xl"
                        >
                          <span className="flex items-center justify-center gap-3">
                            <Trash2 className="h-6 w-6" /> Olib tashlash
                          </span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <div className="border-t border-gray-200 my-20"></div>

        <section className="max-w-3xl mx-auto bg-white rounded-2xl shadow-xl p-8 sm:p-10">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-800 mb-8 flex items-center gap-4">
            <ShoppingCart className="h-9 w-9 text-pink-500" /> Savat
          </h2>
          {cart.length === 0 ? (
            <p className="text-gray-500 text-center py-12 text-xl">
              Savat bo&apos;sh. Mahsulot qo&apos;shing!
            </p>
          ) : (
            <>
              <ul className="space-y-6 mb-8">
                {cart.map((item) => (
                  <li
                    key={item.id}
                    className="flex items-center justify-between pb-4 border-b border-gray-100 last:border-b-0 last:pb-0"
                  >
                    <div className="flex items-center gap-5">
                      <img
                        src={resolveImage(item.image) || "/placeholder.svg"}
                        alt={`Mahsulot ID: ${item.id}`}
                        width={80}
                        height={80}
                        className="rounded-lg object-cover aspect-square shadow-sm"
                        loading="lazy" // Optimize image loading
                      />
                      <div>
                        <span className="font-medium text-gray-900 text-lg">
                          Mahsulot ID: {item.id}
                        </span>
                        <span className="text-gray-600 ml-3 text-lg">
                          x {item.quantity}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="font-bold text-xl text-pink-600">
                        {(item.price * item.quantity).toLocaleString()}{" "}
                        so&apos;m
                      </span>
                      <button
                        onClick={() => updateCart(item, -item.quantity)}
                        className="p-2 rounded-full text-red-500 hover:bg-red-50 transition-colors focus:outline-none focus:ring-2 focus:ring-red-300"
                        aria-label={`Remove product ID ${item.id} from cart`}
                      >
                        <Trash2 className="h-6 w-6" />
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
              <div className="flex justify-between items-center font-bold text-2xl sm:text-3xl pt-6 border-t border-gray-200">
                <span>Jami:</span>
                <span className="text-pink-600">
                  {calculateTotal().toLocaleString()} so&apos;m
                </span>
              </div>
              <div className="flex flex-col gap-5 mt-10">
                <button
                  onClick={sendOrder}
                  disabled={cart.length === 0}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-semibold text-xl transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                >
                  🚚 Buyurtma berish
                </button>
              </div>
            </>
          )}
        </section>
      </main>

      <footer className="text-center text-gray-400 text-base mt-24">
        <p>
          &copy; {new Date().getFullYear()} Gullar do‘koni. Barcha huquqlar
          himoyalangan.
        </p>
      </footer>
    </div>
  );
}
